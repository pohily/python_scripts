from collections import defaultdict, namedtuple
from configparser import ConfigParser
from datetime import datetime
from sys import argv

import requests
from jira import JIRA

from merge_requests import make_rc, make_mr_to_staging, delete_create_RC, PRIORITY, master_to_slov
from send_notifications import ISSUE_URL, RELEASE_URL, REMOTE_LINK, GIT_LAB, STATUS_FOR_RELEASE

docker = False # флаг наличия мерджей на докер
confluence = '' # ссылка на отчет о тестировании
Merge_request = namedtuple('Merge_request', ['url', 'iid', 'project', 'issue']) # iid - номер МР в url'е, project - str


def get_release_details(config, jira):
    try:
        # откуда происходит ввод названия релиза
        COMMAND_LINE_INPUT = eval(config['options']['COMMAND_LINE_INPUT'])
        if COMMAND_LINE_INPUT:
            release_input = argv[1]
        else:
            release_input = 'ru.5.6.10'
    except IndexError:
        raise Exception('Enter release name')
    fix_issues = jira.search_issues(f'fixVersion={release_input}')
    fix_id = jira.issue(fix_issues.iterable[0]).fields.fixVersions[0].id
    return release_input, fix_id, fix_issues


def get_merge_requests(issue_number):
    """ Ищет ссылки на мердж реквесты в задаче и возвращает список ссылок и проектов"""
    result = []
    links_json = requests.get(url=REMOTE_LINK.format(issue_number),
                                 auth=(config['user_data']['login'], config['user_data']['jira_password'])).json()
    for link in links_json:
        url_parts = link['object']['url'].split('/')
        global confluence
        if not confluence:
            if 'confluence' in link['object']['url'] and link['relationship'] == "mentioned in":
                confluence = link['object']['url']
        if len(url_parts) < 6:
            continue
        if 'docker' in link['object']['url']:
            global docker
            docker = True
        project = f'{url_parts[4]}'
        iid = url_parts[6]
        merge_link = Merge_request(link['object']['url'], iid, project, issue_number)
        if GIT_LAB in merge_link.url:
            result.append(merge_link)
    return result


def get_links(config, merges):
    """ принимает список кортежей. заполняет таблицу ссылками на МР SLOV -> RC, и статусами МР Master -> SLOV и SLOV -> RC """
    result = ''
    start = True # флаг первого МР, если их в задаче несколько
    for merge in merges:
        if not start: # если МР не первый - добавляем перенос на следующую строку и две пустых ячейки
            result += '\n|  |  |'
        url_parts = merge.url.split('/')
        table_project = f'{url_parts[3]}/{url_parts[4]}'
        result += f'[{table_project}/{merge.iid}|{merge.url}]|'
        #
        #           Подливаем Мастер в текущую задачу в RC. Выводим статус в таблицу
        #
        print_stage(f'Подливаем Мастер в {issue_number}')
        status = master_to_slov(config, merge)
        result += f'{status}|'
        print_stage(f'{status}')
        #
        #           Пытаемся сделать MR из текущей задачи в RC. Выводим статус в таблицу
        #
        print_stage(f'Пытаемся сделать MR из {issue_number} в {RC_name}')
        status = make_rc(config, merge, RC_name)
        result += f'{status}|'
        print_stage(f'{status}')
        start = False
    return result


def print_stage(text):
    print(f'{datetime.now().strftime("%H:%M:%S")} {text}')


if __name__ == '__main__':
    with open('message.txt', 'w') as file:
        config = ConfigParser()
        config.read('config.ini')
        jira_options = {'server': 'https://jira.4slovo.ru/'}
        jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
        #
        #           Определяем состав релиза
        #
        print_stage('Определяем состав релиза')
        release_name, release_id, release_issues = get_release_details(config, jira)
        RC_name = f'rc-{release_name.replace(".", "-")}'
        #
        #           До таблицы
        #
        message = f"[Состав релиза:|{RELEASE_URL.format(release_id)}]\r\n\r\n\r\n" \
                  f"||№||Задача||Мердж реквесты SLOV -> RC||Подлит свежий мастер, статус||Статус мердж реквеста SLOV -> RC||\r\n"
        #
        #           Выбираем задачи для релиза в нужных статусах
        #
        print_stage('Выбираем задачи для релиза в нужных статусах')
        issues_list = {}
        for issue in release_issues:
            if 'сборка' not in issue.fields.summary.lower() \
                    and issue.fields.status.name in STATUS_FOR_RELEASE \
                    and issue.fields.issuetype.name != 'Defect':
                issues_list[issue.key] = PRIORITY[issue.fields.priority.name]
        #
        #           Собираем мердж реквесты
        #
        print_stage('Собираем мердж реквесты')
        merge_requests = defaultdict(list) # словарь- задача: список кортежей ссылок и проектов
        used_projects = set()
        MRless_issues_number = 1
        MRless_issues = []
        if issues_list:
            for issue_number in issues_list:
                MR_count = get_merge_requests(issue_number)
                if not MR_count: # если в задаче нет МР
                    message += f"|{MRless_issues_number}|[{issue_number}|{ISSUE_URL}{issue_number}]| Нет мердж реквестов |(/)|(/)|\r\n"
                    MRless_issues_number += 1
                    MRless_issues.append(issue_number)
                    continue
                for merge in MR_count:
                    if 'commit' in merge.url:
                        continue
                    used_projects.add(merge.project)
                    merge_requests[issue_number].append(merge)

            if MRless_issues:
                for item in MRless_issues:
                    issues_list.pop(item)
        #
        #           Удаляем и создаем RC
        #
        print_stage('Удаляем и создаем RC')
        for project in used_projects:
            delete_create_RC(config, project, RC_name)
        #
        #           Заполняем таблицу
        #
        print_stage('Заполняем таблицу')
        for index, issue_number in enumerate(sorted(issues_list)): # Todo  сортировка задач по приоритету
            message += f"|{index + MRless_issues_number}|[{issue_number}|{ISSUE_URL}{issue_number}]|" \
                       f"{get_links(config, merge_requests[issue_number])}\r\n"

        message += f'\n\r\n\r\n\r[*Отчет о тестировании*.|{confluence}]\n\r\r\n\r\n'
        #
        #           Создаем MR RC -> Staging
        #
        mr_links = make_mr_to_staging(config, used_projects, RC_name)
        #
        #           Docker -> Master
        #
        print_stage('Заполняем ссылки на МР')
        if docker:
            message += '\n*Docker -> Master*\r\n\r'
            for link in mr_links:
                if 'docker' in link:
                    message += f'\n[{link}]\r'
        #
        #           RC -> Staging
        #
        message += '\n\r\n*RC -> Staging*\r\n\r'
        for link in mr_links:
            if 'docker' not in link:
                message += f'\n[{link}]\r'
        #
        #           Staging -> Master
        #
        message += '\n\r\n*Staging -> Master*\r\n\r'
        #
        #           Преддеплойные действия
        #
        print_stage('Заполняем деплойные действия')
        message += '\n\r\n\r'
        #
        #           Постдеплойные действия
        #
        message += '\n\r\n\r'
        #
        #           Вывод результата в Jira
        #
        print_stage('Вывод результата в Jira')
        issue_dict = {
            "fixVersions": [
        {
            "self": f"{RELEASE_URL.format(release_id)}",
            "id": f"{release_id}",
            "name": f"{release_name}",
        }
        ],
            'project': {'key': 'SLOV'},
            'summary': f"Сборка {release_name}",
            'description': f'{message}',
            'issuetype': {'name': 'Задача'},

        }
        CREATE_JIRA_ISSUE = eval(config['options']['CREATE_JIRA_ISSUE'])
        if CREATE_JIRA_ISSUE:
            new_issue = jira.create_issue(fields=issue_dict)
        #
        #           Вывод результата в файл
        #
        file.write(f"""{message}""")

        # тестить не на бою
        # отдельным шагом вливать мастер в слов, потом уже slov -> rc. соответственно переделываем таблицу - новая колонка
        # деплойные действия
        # запуск скрипта на гитлабе вебхуком от жиры
        # развернуть стенд на нужных ветках и запустить тесты в гитлабе и регресс (в Дженкинс?)


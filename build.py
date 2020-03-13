import logging
import shelve
from collections import defaultdict, namedtuple
from configparser import ConfigParser
from sys import argv

import requests
from jira import JIRA

from constants import PROJECTS_NAMES, PROJECTS_NUMBERS, RELEASE_URL, REMOTE_LINK, GIT_LAB, STATUS_FOR_RELEASE, \
    PRIORITY, ISSUE_URL, MR_STATUS
from merge_requests import make_mr_to_rc, make_mr_to_staging, make_mr_to_master, delete_create_RC, merge_rc, \
    is_merged
from send_notifications import get_release_details

docker = False  # флаг наличия мерджей на докер
confluence = ''  # ссылка на отчет о тестировании
Merge_request = namedtuple('Merge_request', ['url', 'iid', 'project', 'issue'])  # iid - номер МР в url'е, project - int


def get_merge_requests(config, issue_number):
    """ Ищет ссылки на невлитые МР в задаче и возвращает их список """
    result = []
    links_json = requests.get(url=REMOTE_LINK.format(issue_number),
                                 auth=(config['user_data']['login'], config['user_data']['jira_password'])).json()
    for link in links_json:
        global confluence
        if not confluence:
            if 'confluence' in link['object']['url'] and link['relationship'] == "mentioned in":
                confluence = link['object']['url']
        if 'commit' in link['object']['url'] or GIT_LAB not in link['object']['url']:
            continue
        if 'docker' in link['object']['url']:
            global docker
            docker = True
        url_parts = link['object']['url'].split('/')
        if len(url_parts) < 6:
            continue
        try:
            project = PROJECTS_NAMES[f'{url_parts[3]}/{url_parts[4]}']
        except KeyError as e:
            logging.exception(f'Проверьте задачу {issue_number} - не найден проект {url_parts[3]}/{url_parts[4]}')
            continue
        # в связи с обновлением gitlab поменялись url 11/03/20:
        if GIT_LAB in link['object']['url'] and url_parts[6].isdigit():
            iid = url_parts[6]
        elif GIT_LAB in link['object']['url'] and url_parts[7].isdigit():
            iid = url_parts[7]
        else:
            logging.warning(f"Проверьте ссылку {link['object']['url']} в задаче {issue_number}")
            continue
        merge = Merge_request(link['object']['url'], iid, project, issue_number)
        if not is_merged(config, merge):
            result.append(merge)
    return result


def get_links(config, merges):
    """ принимает список кортежей МР одной задачи. Делает МР SLOV -> RC.
    Заполняет таблицу ссылками на SLOV -> RC и статусами SLOV -> RC """

    statuses = {}  # предварительно собираем статусы, затем все сразу вписываем в таблицу
    conflict = False  # флаг наличия конфликтов с RC
    for index, merge in enumerate(merges):
        #
        #           Пытаемся создать MR из текущей задачи в RC. Выводим статус в таблицу
        #
        logging.info(f'Пытаемся сделать MR из {merge.issue} в {RC_name} в {PROJECTS_NUMBERS[merge.project]}')

        status, url, mr = make_mr_to_rc(config, merge, RC_name)
        if status == MR_STATUS['cannot_be_merged']:
            conflict = True

        statuses[index] = [status]  # 0
        statuses[index].append(mr)  # 1
        url_parts = url.split('/')
        # в связи с обновлением gitlab поменялись url 11/03/20:
        if GIT_LAB in url and url_parts[6].isdigit():
            iid = url_parts[6]
        elif GIT_LAB in url and url_parts[7].isdigit():
            iid = url_parts[7]
        else:
            logging.exception(f'Проверьте задачу {issue_number} - некорректная ссылка {url}')
            continue
        statuses[index].append(f'[{url_parts[3]}/{url_parts[4]}/{iid}|{url}]')  # 2
        logging.info(status)
    #
    #           Мержим MR из текущей задачи в RC
    #
    if conflict:
        status = '(x) Не влит'
    else:
        status = '(/) Влит'
    for line in range(len(statuses)):
        statuses[line].append(status)  # 3
        if not conflict:
            mr = statuses[line][1]
            logging.info(f"Мержим {issue_number} в {RC_name} в {mr.attributes['references']['full']}")
            merge_rc(config, mr)

    result = ''
    start = True  # флаг первого МР, если их в задаче несколько
    # 0 - статус slov -> RC, 1 - mr, 2 - MR url, 3 - влит/не влит
    for line in range(len(statuses)):
        if not start: # если МР не первый - добавляем перенос на следующую строку и три пустых ячейки
            result += f'\n|  |  |  |'
        result += f'{statuses[line][2]}|{statuses[line][0]}{statuses[line][3]}|'
        start = False
    return result


if __name__ == '__main__':
    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)
    logging.info('--------------Начало сборки----------------')
    with open('logs/message.txt', 'w') as file:
        config = ConfigParser()
        config.read('config.ini')
        jira_options = {'server': 'https://jira.4slovo.ru/'}
        jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
        #
        #           Определяем состав релиза
        #
        logging.info('Определяем состав релиза')
        _, release_name, _, release_issues, release_id = get_release_details(config, jira)
        RC_name = f'rc-{release_name.replace(".", "-")}'
        #
        #           До таблицы
        #
        message = f"[*Состав релиза:*|{RELEASE_URL.format(release_id)}]\r\n" \
                  f"||№||Задача||Приоритет||Мердж реквесты SLOV -> RC||Статус мердж реквеста SLOV -> RC||\r\n"
        #
        #           Выбираем задачи для релиза в нужных статусах
        #
        logging.info(f'Выбираем задачи для релиза {release_name} в нужных статусах')
        issues_list = {}
        before_deploy = []
        post_deploy = []
        for issue in release_issues:
            if 'сборка' not in issue.fields.summary.lower() and issue.fields.status.name in STATUS_FOR_RELEASE:
                issues_list[issue.key] = PRIORITY[issue.fields.priority.name]
                bd = issue.fields.customfield_15303  # переддеплойные действия
                if bd:
                    before_deploy.append((issue.key, bd))
                pd = issue.fields.customfield_15302  # постдеплойные действия
                if pd:
                    post_deploy.append((issue.key, pd))
        #
        #           Собираем мердж реквесты
        #
        logging.info('Собираем мердж реквесты')
        merge_requests = defaultdict(list)  # словарь- задача: список кортежей ссылок и проектов
        used_projects = set()  # сет проектов всего затронутых в релизе
        MRless_issues_number = 1
        MRless_issues = []
        if issues_list:
            for issue_number in issues_list:
                MR_count = get_merge_requests(config, issue_number)  # возвращаются только невлитые МР
                if not MR_count: # если в задаче нет МР вносим задачу в таблицу
                    message += f"|{MRless_issues_number}|[{issue_number}|{ISSUE_URL}{issue_number}]|" \
                               f"{issues_list[issue_number]}| Нет изменений |(/)|\r\n"
                    MRless_issues_number += 1
                    MRless_issues.append(issue_number)
                    continue

                issue_projects = set()  # сет проектов всего затронутых в задаче
                for merge in MR_count:
                    used_projects.add(merge.project)
                    if merge.project not in issue_projects:  # проверяем не было ли в этой задаче нескольких МР в одном
                        issue_projects.add(merge.project)    # проекте, если несколько - берем один
                        merge_requests[issue_number].append(merge)

            if MRless_issues:  # убираем задачу без МР из списка задач для сборки RC
                for item in MRless_issues:
                    issues_list.pop(item)
        with shelve.open('logs/used_projects') as projects:  # сохраняем использованные проекты на диске
            projects[f'{RC_name}'] = list(used_projects)
        #
        #           Удаляем и создаем RC
        #
        logging.info('Удаляем и создаем RC')
        for project in used_projects:
            delete_create_RC(config, project, RC_name)
        #
        #           Заполняем таблицу
        #
        logging.info('Заполняем таблицу')  # делаем МР в RC и заполняем таблицу ссылками и статусами МР
        for index, issue_number in enumerate(sorted(issues_list)):
            priority = issues_list[issue_number]
            result = get_links(config, merge_requests[issue_number])
            message += f"|{index + MRless_issues_number}|[{issue_number}|{ISSUE_URL}{issue_number}]|{priority}|{result}\r\n"

        if confluence:
            message += f'\n\r[*Отчет о тестировании*.|{confluence}]\n\r'
        #
        #           Создаем MR RC -> Staging для всех проектов (передумали вычитать проекты с конфликтами)
        #
        logging.info('Делаем МР RC -> Staging')
        staging_links = make_mr_to_staging(config, used_projects, RC_name, docker)
        #
        #           Docker -> Master
        #
        logging.info('Заполняем ссылки на МР RC -> Staging, Staging -> Master')
        if docker:
            message += '\r\n*Docker -> Master*\r\n'
            for link in staging_links:
                if 'docker' in link:
                    message += f'\n[{link}]\r'
        #
        #           RC -> Staging
        #
        message += '\n\r*RC -> Staging*\r\n'
        for link in staging_links:
            if 'docker' not in link:
                message += f'\n[{link}]\r'
        #
        #           Создаем MR Staging -> Master
        #
        logging.info('Делаем МР Staging -> Master')
        master_links = make_mr_to_master(config, used_projects)
        #
        #           Staging -> Master
        #
        message += '\n\r*Staging -> Master*\r\n'
        for link in master_links:
            message += f'\n[{link}]\r'
        #
        #           Преддеплойные действия
        #
        logging.info('Заполняем деплойные действия')
        message_before_deploy = ''
        if before_deploy:
            for issue in before_deploy:
                message_before_deploy += f'* *{issue[0]}*: {issue[1]}\r\n'
        #
        #           Постдеплойные действия
        #
        message_post_deploy = ''
        if post_deploy:
            for issue in post_deploy:
                message_post_deploy += f'* *{issue[0]}*: {issue[1]}\r\n'
                #
        #           Вывод результата в Jira
        #
        CREATE_JIRA_ISSUE = eval(config['options']['CREATE_JIRA_ISSUE'])
        if CREATE_JIRA_ISSUE:
            logging.info('Вывод результата в Jira')
            existing_issue = jira.search_issues(f'project=SLOV AND summary ~ "Сборка {release_name}"')
            if existing_issue:
                existing_issue = existing_issue[0]
                existing_issue.update(fields={
                    'description': message,
                    'customfield_15303': message_before_deploy,
                    'customfield_15302': message_post_deploy,
                })
            else:
                issue_dict = {
                    "fixVersions": [{"name": release_name,}],
                    'project': {'key': 'SLOV'},
                    'summary': f"Сборка {release_name}",
                    'description': message,
                    'issuetype': {'name': 'RC'},  #  специальный тип задачи для сборок
                    'customfield_15303': message_before_deploy,
                    'customfield_15302': message_post_deploy,
                }
                new_issue = jira.create_issue(fields=issue_dict)
        #
        #           Вывод результата в файл
        #
        file.write(message)

        #todo
        # # запуск скрипта на гитлабе вебхуком от жиры
        # развернуть стенд на нужных ветках и запустить тесты в гитлабе и регресс (в Дженкинс?)

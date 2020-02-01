from collections import defaultdict, namedtuple
from sys import argv

from configparser import ConfigParser
from jira import JIRA
import requests

from send_notifications import ISSUE_URL, RELEASE_URL, REMOTE_LINK, GIT_LAB, STATUS_FOR_RELEASE

docker = False # флаг наличия мерджей на докер
Merge_request = namedtuple('Merge_request', ['url', 'project'])

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
        merge_link = Merge_request(link['object']['url'], link['object']['title'])
        if GIT_LAB in merge_link.url:
            result.append(merge_link)
    return result


def get_links(merges):
    """ принимает список кортежей. возвращает ссылки на мерджи SLOV -> RC для таблицы """
    result = ''
    start = True
    for merge in merges:
        if not merge.url:
            return '-' # если в задаче нет мердж реквеста
        if start:
            result += f'[{merge.project}|{merge.url}]'
            start = False
        else:
            result += f'\r[{merge.project}|{merge.url}]'
    return result


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    jira_options = {'server': 'https://jira.4slovo.ru/'}
    jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
    release_name, release_id, release_issues = get_release_details(config, jira)
    #
    #           До таблицы
    #
    message = f"Состав релиза:\r\n\r\n[{RELEASE_URL.format(release_id)}]\r\n\r\n" \
              f"||№||Задача||Мердж реквесты SLOV -> RC||Подлит свежий мастер, нет конфликтов||\r\n"
    #
    #           Выбираем задачи для релиза в нужных статусах
    #
    issues_list = {}
    for issue in release_issues:
        if 'сборка' not in issue.fields.summary.lower() \
                and issue.fields.status.name in STATUS_FOR_RELEASE \
                and issue.fields.issuetype.name != 'Defect':
            issues_list[issue.key] = issue.fields.summary
    #
    #           Собираем мердж реквесты
    #
    merge_requests = defaultdict(list) # словарь- задача: список кортежей ссылок и проектов
    docker_merges = [] # список мерджей докера
    if issues_list:
        for issue_number in issues_list:
            for merge in get_merge_requests(issue_number):
                if 'commit' in merge.url:
                    continue
                elif 'docker' in merge.url:
                    docker = True
                    docker_merges.append(merge.url)
                merge_requests[issue_number].append(merge)
    #
    #           Заполняем таблицу
    #
    for index, issue_number in enumerate(sorted(issues_list)):
        message += f"|{index + 1}|[{issue_number}|{ISSUE_URL}{issue_number}]|{get_links(merge_requests[issue_number])}| |\r\n"

    message += '\n\r'
    #
    #           Создаем RC
    #
    pass
    #
    #           Docker -> Master
    #
    if docker:
        message += '\n*Docker -> Master*\r\n\r'
        for link in docker_merges:
            message += f'\n{link}\r' # тест (мерджи slov -> rc). потом будем выводить мерджи в мастер
    #
    #           RC -> Staging
    #
    message += '\n\r\n*RC -> Staging*\r\n\r'
    #
    #           Staging -> Master
    #
    message += '\n\r\n*Staging -> Master*\r\n\r'
    #
    #           Staging -> Master
    #
    message += '\n\r\n\r'
    #
    #           Преддеплойные действия
    #
    message += '\n\r\n\r'
    #
    #           Постдеплойные действия
    #
    message += '\n\r\n\r'
    #
    #           Вывод результата в Jira
    #
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
    if not CREATE_JIRA_ISSUE:
        txt = f"""{message}"""
        with open('message.txt', 'w') as file:
            file.write(txt)



    # сделать RC ветки
    # деплойные действия
    # развернуть стенд на нужных ветках и запустить тесты в гитлабе и регресс (в Дженкинс?)


from collections import defaultdict

import configparser
from jira import JIRA
import requests

from send_notifications import RELEASE_ISSUES_URL, ISSUE_URL, RELEASES_LIST_URL, RELEASE_URL, REMOTE_LINK, GIT_LAB, STATUS_FOR_RELEASE
from send_notifications import get_issues

SHOW_SLOV_MERGES = False

def get_merge_requests(issue_number):
    """ Ищет ссылки на мердж реквесты в задаче и возвращает список ссылок """
    result = set()
    links_json = requests.get(url=REMOTE_LINK.format(issue_number),
                                 auth=(config['user_data']['login'], config['user_data']['jira_password'])).json()
    for link in links_json:
        url = link['object']['url']
        if GIT_LAB in url:
            result.add(url)
    return list(result)


def sort_merge_requests(task):
    """ Возвращает словарь списков мерджреквестов, рассортированных по проектам """
    projects = defaultdict(list)
    for links in task:
        for link in links:
            url_parts = link.split('/')
            if 'docker' not in link:
                projects[url_parts[4]].append(link)
            else:
                projects['docker'].append(link)
    return projects


def get_release_id(config):
    try:
        release_input = 'ru.5.6.10'#sys.argv[1]
    except IndexError:
        raise Exception('Enter release name')
    releases_json = requests.get(url=RELEASES_LIST_URL,
                                 auth=(config['user_data']['login'], config['user_data']['jira_password'])).json()
    for release in releases_json:
        if release['name'] == release_input:
             return release['name'], release['id']
    raise Exception('Release not found')


def get_links(merges):
    """ возвращает ссылки на мерджи SLOV -> RC для таблицы """
    result = ''
    start = True
    for link in merges:
        if start:
            result += f'[{link}]|'
            start = False
        else:
            result += f'|\r|||[{link}]|'
    return result


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    release_info = {}
    release_info['name'], release_info['id'] = get_release_id(config)
    issues_of_release_link = RELEASE_ISSUES_URL.format(release_info['name'])
    issues_list = {}
    #
    #           До таблицы
    #
    message = f"Состав релиза:\r\n\r\n[{RELEASE_URL.format(release_info['id'])}]\r\n\r\n||№||Задача||SLOV -> RC||Подлит свежий мастер, нет конфликтов||\r"
    #
    #           Выбираем задачи для релиза в нужных статусах
    #
    for issue in get_issues(config, issues_of_release_link):
        if 'сборка' not in issue['fields']['summary'].lower() and issue['fields']['status']['name'] in STATUS_FOR_RELEASE:
            issues_list[issue['key']] = issue['fields']['summary']
    #
    #           Собираем мердж реквесты
    #
    merge_requests = defaultdict(list)
    if issues_list:
        for issue_number in issues_list:
            for merge in get_merge_requests(issue_number):
                if 'commit' in merge:
                    continue
                merge_requests[issue_number].append(merge)
    projects = sort_merge_requests(merge_requests.values())
    #
    #           Заполняем таблицу
    #
    for index, issue_number in enumerate(sorted(issues_list)):
        message += f"\n|{index + 1}|[{issue_number}|{ISSUE_URL}{issue_number}]|{get_links(merge_requests[issue_number])}|(/)|\r"

    message += '\n\r'
    #
    #           Создаем RC
    #
    pass
    #
    #           Docker -> Master
    #
    if 'docker' in projects:
        docker = True
        message += '\n*Docker -> Master*\r\n\r'
    #
    #           SLOV -> RC
    #
    if SHOW_SLOV_MERGES:
        message += '\n*SLOV -> RC*\r'
        for project in projects:
            if project == 'docker':
                continue
            for merge_request in projects[project]:
                message += f'\n[{merge_request}]\r'
            message += '\n\r'
    #
    #           RC -> Staging
    #
    message += '\n*RC -> Staging*\r\n\r'
    #
    #           Staging -> Master
    #
    message += '\n*Staging -> Master*\r\n\r'
    #
    #           Staging -> Master
    #
    message += '\n\r'
    #
    #           Вывод результата в Jira
    #
    txt = f"""{message}"""
    with open('message.txt', 'w') as file:
        file.write(txt)



    # добавить задачу в жиру, добавить сборочную задачу в релиз
    # сделать RC ветки
    # деплойные действия
    # развернуть стенд на нужных ветках и запустить тесты в гитлабе и регресс (в Дженкинс?)


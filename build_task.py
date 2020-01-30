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
    result = []
    for link in merges:
        result.append(f'<a href="{link}" class="external-link" rel="nofollow">{link}</a><br/>')
    return ''.join(result)


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
    message = f"<p><b>Состав релиза:</b></p><p><a href='{RELEASE_URL.format(release_info['id'])}' " \
              f"class='external-link' rel='nofollow'>{RELEASE_URL.format(release_info['id'])}</a></p>" \
              f"<div class='table-wrap'><table class='confluenceTable'><tbody>" \
              f"<tr><th class='confluenceTh'>№</th>" \
              f"<th class='confluenceTh'>Задача</th>" \
              f"<th class='confluenceTh'>SLOV -&gt; RC</th>" \
              f"<th class='confluenceTh'>Подлит свежий мастер, нет конфликтов</th></tr>"
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
        message += f"<tr><td class='confluenceTd'>{index + 1}</td>" \
                   f"<td class='confluenceTd'><a href='{ISSUE_URL}{issue_number}'title='{issues_list[issue_number]}' " \
                   f"class='issue-link' data-issue-key='{issue_number}'>{issue_number}</a></td>" \
                   f"<td class='confluenceTd'>{get_links(merge_requests[issue_number])}</td>" \
                   f"<td class='confluenceTd'>ок</td></tr>"
    message += '</tbody></table></div>'
    #
    #           Создаем RC
    #
    pass
    #
    #           Docker -> Master
    #
    if 'docker' in projects:
        docker = True
        message += '<p><b>Docker -&gt; Master</b></p>'
    #
    #           SLOV -> RC
    #
    if SHOW_SLOV_MERGES:
        message += '<p></p><p><b>SLOV -&gt; RC</b></p><p></p><p></p>'
        for project in projects:
            if project == 'docker':
                continue
            for merge_request in projects[project]:
                message += f'<p><a href="{merge_request}" class="external-link" rel="nofollow">{merge_request}</a> </p>'
            message += '<br/>'
    #
    #           RC -> Staging
    #
    message += '<p></p><p><b>RC -&gt; Staging</b></p><p></p><p></p>'
    #
    #           Staging -> Master
    #
    message += '<p></p><p></p><p><b>Staging -&gt; Master</b></p><p></p>'
    #
    #           Staging -> Master
    #
    message += '<p></p>'
    #
    #           Вывод результата в Jira
    #
    html = f"""{message}"""
    with open('message.html', 'w') as file:
        file.write(html)



    # добавить задачу в жиру, добавить сборочную задачу в релиз
    # сделать RC ветки
    # деплойные действия
    # развернуть стенд на нужных ветках и запустить тесты в гитлабе и регресс (в Дженкинс?)


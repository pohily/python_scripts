from collections import defaultdict

import configparser
from jira import JIRA
import requests

from send_notifications import RELEASE_ISSUES_URL, ISSUE_URL, RELEASES_LIST_URL, RELEASE_URL, REMOTE_LINK, GIT_LAB, STATUS_FOR_RELEASE
from send_notifications import get_issues


def get_merge_requests(issue_number):
    """ Ищет ссылки на мердж реквесты в задаче и возвращает список ссылок """
    result = set()
    links_json = requests.get(url=REMOTE_LINK.format(issue_number),
                                 auth=(config['user_data']['login'], config['user_data']['jira_password'])).json()
    for link in links_json:
        url = link['object']['url']
        if GIT_LAB in url:
            result.add(url)
    return result


def sort_merge_requests(urls):
    """ Возвращает словарь мерджреквестов, рассортированных по проектам """
    projects = defaultdict(list)
    for url in urls:
        url_parts = url.split('/')
        if 'commit' in url:
            continue
        if 'docker' not in url:
            projects[url_parts[4]].append(url)
        else:
            projects['docker'].append((url))
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
           f"<div class='table-wrap'><table class='confluenceTable'><tbody>"\
           f"<tr><th class='confluenceTh'>№</th><th class='confluenceTh'>Задача</th>" \
           f"<th class='confluenceTh'>Подлит свежий мастер, нет конфликтов</th></tr>"
    #
    #           Выбираем задачи для релиза в нужных статусах
    #
    for issue in get_issues(config, issues_of_release_link):
        if 'сборка' not in issue['fields']['summary'].lower() and issue['fields']['status']['name'] in STATUS_FOR_RELEASE:
            issues_list[issue['key']] = issue['fields']['summary']
    #
    #           Заполняем таблицу
    #
    merge_requests = set()
    if issues_list:
        for number, issue_number in enumerate(sorted(issues_list)):
            merge_requests |= (get_merge_requests(issue_number))
            message += f"<tr><td class='confluenceTd'>{number + 1}</td>" \
                       f"<td class='confluenceTd'><a href='{ISSUE_URL}{issue_number}" \
                       f"'title='{issues_list[issue_number]}' class='issue-link' data-issue-key='{issue_number}'" \
                       f">{issue_number}</a></td><td class='confluenceTd'></td></tr>"
        projects = sort_merge_requests(merge_requests)
        message += '</tbody></table></div>'
        #
        #           Docker -> Master
        #
        if 'docker' in projects:
            docker = True
            message += '<p><b>Docker -&gt; Master</b></p>'
            for merge_request in projects['docker']:
                message += f'<p><a href="{merge_request}" class="external-link" rel="nofollow">{merge_request}</a> </p>'
        #
        #           SLOV -> RC
        #
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


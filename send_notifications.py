from configparser import ConfigParser
from smtplib import SMTP
from sys import argv
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText

import requests

ISSUE_API_LINK = 'https://jira.4slovo.ru/rest/api/latest/issue/{}'
ISSUE_URL = 'https://jira.4slovo.ru/browse/'
GIT_LAB = 'https://gitlab'
RELEASE_ISSUES_URL = 'https://jira.4slovo.ru/rest/api/latest/search?jql=fixVersion={}'
RELEASES_LIST_URL = 'https://jira.4slovo.ru/rest/api/latest/project/SLOV/versions'
RELEASE_URL = 'https://jira.4slovo.ru/projects/SLOV/versions/{}'
REMOTE_LINK = 'https://jira.4slovo.ru/rest/api/latest/issue/{}/remotelink'
STATUS_FOR_RELEASE = ['Released to production', 'Passed QA', 'In regression test', 'Ready for release', 'Закрыт', 'Fixed']
SMTP_PORT = 587
SMTP_SERVER = 'smtp.4slovo.ru'


def get_release_info(config):
    try:
        release_input = argv[1]
    except IndexError:
        raise Exception('Enter release name')
    releases_json = requests.get(url=RELEASES_LIST_URL,
                                 auth=(config['user_data']['login'], config['user_data']['jira_password'])).json()
    for release in releases_json:
        if release['name'] == release_input:
            if 'ru' in release_input.lower():
                release_country = 'Россия'
            elif 'kz' in release_input.lower():
                release_country = 'Казахстан'
            else:
                release_country = 'Грузия'
            return datetime.strptime(release['releaseDate'], '%Y-%m-%d').strftime('%d.%m.%Y'), release[
                'name'], release_country, release['id']
    raise Exception('Release not found')


def get_release_message(release_info):
    return 'Уважаемые коллеги, добрый день! <br>{release_date} состоялся выпуск релиза для страны {release_country} \
    {release_name}<br>Состав выпуска:<br><br>'.format(
        release_name=release_info['name'], release_date=release_info['date'], release_country=release_info['country'])


def get_issues(config, release_url):
    request = requests.get(url=release_url,
                           auth=(config['user_data']['login'], config['user_data']['jira_password']))
    request_issues = request.json()['issues']
    return request_issues


def send_mail(release_info, message, config):
    connection = SMTP(SMTP_SERVER, SMTP_PORT)
    connection.ehlo()
    connection.starttls()
    connection.ehlo()
    connection.login(config['user_data']['login'], config['user_data']['domain_password'])
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['subject'] = Header('Релиз для {}: {}'.format(release_info['country'], release_info['name']), 'utf-8')
    msg['from'] = config['user_data']['login'] + '@4slovo.ru'
    msg['to'] = config['recipients'][release_info['country_key']]
    msg.add_header('Content-Type', 'text/html')
    connection.sendmail(msg['from'], [msg['to']], msg.as_string())
    connection.quit()


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    release_info = {}
    release_info['date'], release_info['name'], release_info['country'], release_info['id'] = get_release_info(config)
    issues_of_release_link = RELEASE_ISSUES_URL.format(release_info['name'])
    issues_list = {}
    message = get_release_message(release_info)
    for issue in get_issues(config, issues_of_release_link):
        if 'сборка' not in issue['fields']['summary'].lower():
            issues_list[issue['key']] = issue['fields']['summary']

    if issues_list:
        for issue_number in issues_list:
            message += f"[<a href='{ISSUE_URL}{issue_number}'>{issue_number}</a>] - {issues_list[issue_number]}<br>"
        if release_info['country'] == 'Россия':
            country_key = 'ru'
        elif release_info['country'] == 'Казахстан':
            country_key = 'kz'
        elif release_info['country'] == 'Грузия':
            country_key = 'ge'
        else:
            raise Exception('Страна для релиза не определена')
        release_info['country_key'] = country_key
        send_mail(release_info, message, config)

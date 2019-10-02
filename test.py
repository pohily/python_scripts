from email.header import Header
from email.mime.text import MIMEText

import requests
import sys
from datetime import datetime
import smtplib
import configparser

RELEASE_ISSUES_URL = 'https://jira.4slovo.ru/rest/api/latest/search?jql=fixVersion={}'
RELEASES_LIST_URL = 'https://jira.4slovo.ru/rest/api/latest/project/SLOV/versions'
ISSUE_URL = 'https://jira.4slovo.ru/browse/'
SMTP_SERVER = 'smtp.4slovo.ru'
SMTP_PORT = 587


def get_release_info(config):
    try:
        release_input = sys.argv[1]
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
                'name'], release_country
    raise Exception('Release not found')


def get_release_message(release_info):
    return 'Уважаемые коллеги, добрый день! <br>{release_date} состоялся выпуск релиза для страны {release_country} \
    {release_name}<br>Состав выпуска:<br><br>'.format(
        release_name=release_info['name'], release_date=release_info['date'], release_country=release_info['country'])


def get_issues(config):
    request = requests.get(url=issues_of_release_link,
                           auth=(config['user_data']['login'], config['user_data']['jira_password']))
    return request.json()['issues']


def send_mail(release_info, message, config):
    connection = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    connection.ehlo()
    connection.starttls()
    connection.ehlo()
    connection.login(config['user_data']['login'], config['user_data']['domain_password'])
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['subject'] = Header('Релиз для {}: {}'.format(release_info['country'], release_info['name']), 'utf-8')
    msg['from'] = config['user_data']['login'] + '@4slovo.ru'
    msg['to'] = config['recipient']['email']
    msg.add_header('Content-Type', 'text/html')
    connection.sendmail(msg['from'], [msg['to']], msg.as_string())
    connection.quit()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    release_info = {}
    release_info['date'], release_info['name'], release_info['country'] = get_release_info(config)
    issues_of_release_link = RELEASE_ISSUES_URL.format(release_info['name'])
    issues_list = {}
    message = get_release_message(release_info)
    for issue in get_issues(config):
        if 'сборка' not in issue['fields']['summary'].lower():
            issues_list[issue['key']] = issue['fields']['summary']

    if issues_list:
        for issue_number in issues_list:
            message += "[<a href='{issue_url}{issue_number}'>{issue_number}</a>] - {issue_title}<br>".format(
                issue_number=issue_number, issue_title=issues_list[issue_number], issue_url=ISSUE_URL)
        send_mail(release_info, message, config)

import configparser
import smtplib
import sys
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText

import requests
from jira import JIRA

from send_notifications import RELEASE_ISSUES_URL, RELEASES_LIST_URL, ISSUE_URL, SMTP_PORT, SMTP_SERVER

RELEASE_URL = 'https://jira.4slovo.ru/projects/SLOV/versions/{}'

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
                'name'], release_country, release['id']
    raise Exception('Release not found')


def get_release_message(release_info):
    return f"<p>Состав релиза:</p><br><p><a href='{RELEASE_URL.format(release_info['id'])}' " \
           f"class='external-link' rel='nofollow'>{RELEASE_URL.format(release_info['id'])}</a></p>" \
           f"<div class='table-wrap'><table class='confluenceTable'><tbody>"\
           f"<tr><th class='confluenceTh'>№</th><th class='confluenceTh'>Задача</th>" \
           f"<th class='confluenceTh'>Подлит свежий мастер, нет конфликтов</th></tr>"



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
    msg['to'] = config['recipients'][release_info['country_key']]
    msg.add_header('Content-Type', 'text/html')
    connection.sendmail(msg['from'], [msg['to']], msg.as_string())
    connection.quit()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    release_info = {}
    release_info['date'], release_info['name'], release_info['country'], release_info['id'] = get_release_info(config)
    issues_of_release_link = RELEASE_ISSUES_URL.format(release_info['name'])
    issues_list = {}
    message = get_release_message(release_info)
    for issue in get_issues(config):
        if 'сборка' not in issue['fields']['summary'].lower():
            issues_list[issue['key']] = issue['fields']['summary']

    if issues_list:
        for number, issue_number in enumerate(sorted(issues_list)):
            message += f"<tr><td class='confluenceTd'>{number + 1}</td>" \
                       f"<td class='confluenceTd'><a href='{ISSUE_URL}{issue_number}'title='{issues_list[issue_number]}' " \
                       f"class='issue-link' data-issue-key='{issue_number}'>{issue_number}</a></td>" \
                       f"<td class='confluenceTd'></td></tr>"
        message += '</div><p></p><p><b>RC -&gt; Staging</b></p><p></p><p></p><p></p><p></p><p><b>Staging -&gt; Master</b></p><p></p>'
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


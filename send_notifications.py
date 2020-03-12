from configparser import ConfigParser
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP
from sys import argv

from jira import JIRA

ISSUE_URL = 'https://jira.4slovo.ru/browse/'
GIT_LAB = 'https://gitlab'
RELEASE_ISSUES_URL = 'https://jira.4slovo.ru/rest/api/latest/search?jql=fixVersion={}'
RELEASE_URL = 'https://jira.4slovo.ru/projects/SLOV/versions/{}'
REMOTE_LINK = 'https://jira.4slovo.ru/rest/api/latest/issue/{}/remotelink'
STATUS_FOR_RELEASE = ['Released to production', 'Passed QA', 'In regression test', 'Ready for release', 'Закрыт', 'Fixed']#, 'In development']
SMTP_PORT = 587
SMTP_SERVER = 'smtp.4slovo.ru'


def get_release_details(config, jira):
    try:
        COMMAND_LINE_INPUT = eval(config['options']['COMMAND_LINE_INPUT'])
        if COMMAND_LINE_INPUT:
            release_input = argv[1]
        else:
            release_input = 'kz.3.14.35'
    except IndexError:
        raise Exception('Enter release name')
    fix_issues = jira.search_issues(f'fixVersion={release_input}')
    fix_date = fix_issues[0].fields.fixVersions[0].releaseDate
    if 'ru' in release_input.lower():
        release_country = 'Россия'
    elif 'kz' in release_input.lower():
        release_country = 'Казахстан'
    else:
        release_country = 'Грузия'
    return datetime.strptime(fix_date, '%Y-%m-%d').strftime('%d.%m.%Y'), release_input, release_country, fix_issues


def get_release_message(release_date, release_country, release_name):
    return f'Уважаемые коллеги, добрый день! <br>{release_date} состоялся выпуск релиза для страны {release_country} \
    {release_name}<br>Состав выпуска:<br><br>'


def send_mail(release_country, release_name, country_key, message, config):
    connection = SMTP(SMTP_SERVER, SMTP_PORT)
    connection.ehlo()
    connection.starttls()
    connection.ehlo()
    connection.login(config['user_data']['login'], config['user_data']['domain_password'])
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['subject'] = Header('Релиз для {}: {}'.format(release_country, release_name), 'utf-8')
    msg['from'] = config['user_data']['login'] + '@4slovo.ru'
    msg['to'] = config['recipients'][country_key]
    msg.add_header('Content-Type', 'text/html')
    connection.sendmail(msg['from'], [msg['to']], msg.as_string())
    connection.quit()


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    jira_options = {'server': 'https://jira.4slovo.ru/'}
    jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
    release_date, release_name, release_country, release_issues = get_release_details(config, jira)
    issues_of_release_link = RELEASE_ISSUES_URL.format(release_name)
    issues_list = {}
    message = get_release_message(release_date, release_country, release_name)
    for issue in release_issues:
        if 'сборка' not in issue.fields.summary.lower():
            issues_list[issue.key] = issue.fields.summary

    if issues_list:
        for issue_number in sorted(issues_list):
            message += f"<a href='{ISSUE_URL}{issue_number}'>{issue_number}</a> - {issues_list[issue_number]}<br>"
        if release_country == 'Россия':
            country_key = 'ru'
        elif release_country == 'Казахстан':
            country_key = 'kz'
        elif release_country == 'Грузия':
            country_key = 'ge'
        else:
            raise Exception('Страна для релиза не определена')
        send_mail(release_country, release_name, country_key, message, config)


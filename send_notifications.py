import logging
from configparser import ConfigParser
from datetime import datetime
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP
from sys import argv
import os

from jira import JIRA

from constants import SMTP_PORT, SMTP_SERVER, ISSUE_URL, RELEASE_ISSUES_URL, JIRA_SERVER


def get_release_details(config, jira, date=False, release=False):
    """ Получает имя релиза из коммандной строки, либо передается агрументом, либо в тестовом режиме - хардкод
        Возвращает: дату, имя, страну, задачи релиза и id """

    if not release:
        try:
            COMMAND_LINE_INPUT = eval(config['options']['COMMAND_LINE_INPUT'])
            if COMMAND_LINE_INPUT:
                release_input = argv[1]
            else:
                release_input = 'ru.5.7.35'
        except IndexError:
            logging.exception('Введите имя релиза!')
            raise Exception('Введите имя релиза!')
    else:
        release_input = release
    fix_issues = jira.search_issues(f'fixVersion={release_input}')
    if date:
        try:
            fix_date = fix_issues[0].fields.fixVersions[0].releaseDate
            fix_date = datetime.strptime(fix_date, '%Y-%m-%d').strftime('%d.%m.%Y')
        except (AttributeError, UnboundLocalError, TypeError):
            fix_date = None
            logging.exception(f'Релиз {release_input} еще не выпущен!')
    else:
        fix_date = None
    if 'ru' in release_input.lower():
        release_country = 'Россия'
    elif 'kz' in release_input.lower():
        release_country = 'Казахстан'
    else:
        release_country = 'Грузия'
    fix_id = fix_issues[0].fields.fixVersions[0].id
    return fix_date, release_input, release_country, fix_issues, fix_id


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
    logging.info('Высылаем письмо')
    connection.sendmail(msg['from'], [msg['to']], msg.as_string())
    connection.quit()


if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.mkdir(os.getcwd() + '/log')
    config = ConfigParser()
    config.read('config.ini')
    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)
    logging.info('--------------Формируем письмо----------------')
    jira_options = {'server': JIRA_SERVER}
    jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
    release_date, release_name, release_country, release_issues, _ = get_release_details(config, jira, date=True)
    issues_of_release_link = RELEASE_ISSUES_URL.format(release_name)
    issues_list = {}
    message = get_release_message(release_date, release_country, release_name)
    for issue in release_issues:
        if 'сборка' not in issue.fields.summary.lower():
            issues_list[issue.key] = issue.fields.summary

    if issues_list and release_date:
        for issue_number in sorted(issues_list):
            message += f"<a href='{ISSUE_URL}{issue_number}'>{issue_number}</a> - {issues_list[issue_number]}<br>"
        if release_country == 'Россия':
            country_key = 'ru'
        elif release_country == 'Казахстан':
            country_key = 'kz'
        elif release_country == 'Грузия':
            country_key = 'ge'
        else:
            logging.exception('Страна для релиза не определена')
            raise Exception('Страна для релиза не определена')
        send_mail(release_country, release_name, country_key, message, config)


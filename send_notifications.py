import logging
import os
from email.header import Header
from email.mime.text import MIMEText
from smtplib import SMTP

from constants import SMTP_PORT, SMTP_SERVER, ISSUE_URL
from merge_requests import Build


def get_release_message(release_date, release_country, release_name):
    return f'Уважаемые коллеги, добрый день! <br>{release_date} состоялся выпуск релиза для страны {release_country} \
    {release_name}<br>Состав выпуска:<br><br>'


def send(release_country, release_name, country_key, message, config):
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


def main():
    build = Build()
    os.makedirs('logs', exist_ok=True)
    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)
    logging.info('--------------Формируем письмо----------------')
    release_date, release_name, release_country, release_issues, _ = build.get_release_details(date=True)
    logging.info(f'для релиза {release_name}')
    issues_list = {}
    message = get_release_message(release_date, release_country, release_name)
    for issue in release_issues:
        if 'сборка' not in issue.fields.summary.lower():
            issues_list[issue.key] = issue.fields.summary

    if issues_list and release_date:
        for index, issue_number in enumerate(sorted(issues_list)):
            message += f"{index + 1}. <a href='{ISSUE_URL}{issue_number}'>{issue_number}</a> - {issues_list[issue_number]}<br>"
        if release_country == 'Россия':
            country_key = 'ru'
        elif release_country == 'Казахстан':
            country_key = 'kz'
        elif release_country == 'Грузия':
            country_key = 'ge'
        else:
            logging.exception('Страна для релиза не определена')
            raise Exception('Страна для релиза не определена')
        send(release_country, release_name, country_key, message, build.config)


if __name__ == '__main__':
    main()

import logging
import os
from email.header import Header
from email.mime.text import MIMEText
from functools import lru_cache
from smtplib import SMTP

from build import Build
from constants import SMTP_PORT, SMTP_SERVER, ISSUE_URL, PROJECTS_NUMBERS


def get_release_message(release_date, release_country, release_name):
    return f'Уважаемые коллеги, добрый день! <br>{release_date} состоялся выпуск релиза для {release_country} \
    {release_name}<br>Состав выпуска:<br><br>'


def send(release_country, release_name, country_key, message, config):
    with SMTP(SMTP_SERVER, SMTP_PORT) as connection:
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


def main():
    build = Build()

    @lru_cache(maxsize=None)
    def get_epic(epic_issue_name):
        epic_issue = build.jira.search_issues(f'key={epic_issue_name}')[0]
        return epic_issue.fields.customfield_10008

    os.makedirs('logs', exist_ok=True)
    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)
    logging.info('--------------Формируем письмо----------------')
    release_date, release_name, release_country, release_issues, _ = build.get_release_details(date=True)

    logging.info('создаем в Gitlab теги с именем релиза в каждом измененном проекте')
    issues, _, _ = build.get_issues_list_and_deploy_actions(release_issues)
    _, release_projects, _, _ = build.get_mrs_and_used_projects(issues, '', return_merged=True)
    for pr in release_projects:
        project = build.gitlab.projects.get(pr)
        logging.info(f'make tag {release_name} for {PROJECTS_NUMBERS[pr]}')
        try:
            project.tags.create({'tag_name': release_name, 'ref': 'master'})
        except Exception:
            logging.error(f'Не создан tag {release_name} for {PROJECTS_NUMBERS[pr]}')

    issues_list = {}
    message = get_release_message(release_date, release_country, release_name)
    for issue in release_issues:
        if 'сборка' not in issue.fields.summary.lower():
            epic = ''
            if issue.fields.customfield_10009:
                epic = get_epic(epic_issue_name=issue.fields.customfield_10009)
            issuetype = issue.fields.issuetype.name
            priority = issue.fields.priority.name
            summary = issue.fields.summary
            issues_list[issue.key] = (epic, issuetype, priority, summary)

    if issues_list and release_date:
        message += '<table border="1" cellpadding="5" style="border: 1px solid black;">'
        for index, issue_number in enumerate(sorted(issues_list)):
            epic = ''
            if issues_list[issue_number][0]:
                epic = f'{issues_list[issue_number][0]} '
            message += f"<tr>" \
                       f"<td>{index + 1}.</td>" \
                       f"<td>  <a href='{ISSUE_URL}{issue_number}'>{issue_number}</a> </td>" \
                       f"<td>  {epic} </td>" \
                       f"<td>  {issues_list[issue_number][1]} </td>" \
                       f"<td>  {issues_list[issue_number][2]} </td>" \
                       f"<td>  {issues_list[issue_number][3]} </td>" \
                       f"</tr>"
        message += "</table>"
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

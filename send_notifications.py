import logging
import os
from functools import lru_cache

from envelopes import Envelope

from build import Build
from constants import SMTP_PORT, SMTP_SERVER, ISSUE_URL, PROJECTS_NUMBERS, DOMAIN


def get_release_message(release_date, release_country, release_name):
    return f'Уважаемые коллеги, добрый день! <br>{release_date} состоялся выпуск релиза для {release_country} \
    {release_name}<br>Состав выпуска:<br><br>'


def send(release_country, release_name, country_key, message, config):
    envelope = Envelope(
        from_addr=(config['user_data']['login'] + f'@{DOMAIN}'),
        to_addr=(config['recipients'][country_key]),
        subject=f'Релиз для {release_country}: {release_name}',
        html_body=message
        # bcc_addr=config['recipients']['bcc']
    )
    logging.info('Высылаем письмо')
    envelope.send(SMTP_SERVER, SMTP_PORT,
                  login=config['user_data']['login'], password=config['user_data']['domain_password'], tls=True)


def main():
    build = Build()

    @lru_cache(maxsize=None)
    def get_epic(epic_issue_name):
        epic_issue = build.jira.search_issues(f'key={epic_issue_name}')[0]
        return epic_issue.fields.customfield_10008

    os.makedirs('logs', exist_ok=True)
    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)21s[LINE:%(lineno)3d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)
    logging.info('--------------Формируем письмо----------------')
    release_date, release_name, release_country, release_issues, _ = build.get_release_details(date=True)

    if release_date:
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
        build_issue = ''
        for issue in release_issues:
            if issue.fields.issuetype.name == 'Defect':
                continue
            if 'сборка' in issue.fields.summary.lower():
                build_issue = issue.key
                continue
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
            if release_country == 'России':
                country_key = 'ru'
            elif release_country == 'Казахстана':
                country_key = 'kz'
            elif release_country == 'Грузии':
                country_key = 'ge'
            else:
                logging.exception('Страна для релиза не определена')
                raise Exception('Страна для релиза не определена')
            message += '<br><br>Релиз затронул следующие проекты:<ul style="list-style-type:circle">'
            for project in release_projects:
                message += f'<li> {PROJECTS_NUMBERS[project]}</li>'
            message += '</ul>'
            message += f"Сборка: <a href='{ISSUE_URL}{build_issue}'>{build_issue}</a>"
            send(release_country, release_name, country_key, message, build.config)
    else:
        logging.exception('Сначала надо отметить релиз как выпущенный и выбрать дату релиза в Jira')


if __name__ == '__main__':
    main()

import logging
from configparser import ConfigParser
from itertools import chain
from re import sub
import os

import gitlab
from jira import JIRA

from build import get_merge_requests
from constants import STATUS_FOR_RELEASE, PROJECTS_COUNTRIES, PROJECTS_NUMBERS, JIRA_SERVER, TESTERS
from send_notifications import get_release_details
from merge_requests import get_merge_request_details

""" Показывает статистику по запрошенному релизу: количество задач, проектов и названия проектов, 
также показываются задачи, которые не подходят для данного релиза (неправильная страна).
Показывает репозитории, к которым необходимо получить доступ для сборки релиза.
Показывает мердж конфликты, если такие есть"""


def main():
    os.makedirs('logs', exist_ok=True)
    config = ConfigParser()
    config.read('config.ini')
    jira_options = {'server': JIRA_SERVER}
    jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)
    _, release_input, _, fix_issues, _ = get_release_details(config, jira)
    logging.info(f'Статистика релиза {release_input}')
    used_projects = set()
    issue_count = 0
    wrong_release_issues = set()
    country = release_input.split('.')[0].lower()
    before_deploy = []
    post_deploy = []
    for issue_number in fix_issues:
        if issue_number.fields.status.name in STATUS_FOR_RELEASE:
            issue_count += 1
            bd = issue_number.fields.customfield_15303  # переддеплойные действия
            if bd:
                before_deploy.append((issue_number.key, bd))
            pd = issue_number.fields.customfield_15302  # постдеплойные действия
            if pd:
                post_deploy.append((issue_number.key, pd))
        else:
            continue
        MR_count = get_merge_requests(config, issue_number)
        for merge in MR_count:
            status, _, _, _ = get_merge_request_details(config, merge)
            if status != '(/) Нет конфликтов, ':
                logging.exception(f'\033[31m Конфликт в задаче {merge.issue} в мердж реквесте {merge.url}\033[0m')
            used_projects.add(merge.project)
            try:
                if country not in PROJECTS_COUNTRIES[merge.project].lower():
                    issue = merge.issue.key
                    wrong_release_issues.add(issue)
            except:
                logging.exception(f'У вас нет доступа к проекту {PROJECTS_COUNTRIES[merge.project]}')
    projects = [PROJECTS_NUMBERS[pr] for pr in used_projects]
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    user_id = TESTERS[config['user_data']['login']]
    reporter = []
    for project in projects:
        pr = gl.projects.get(project)
        member = pr.members.get(user_id)
        access_level = member.attributes['access_level']
        if access_level < 30:
            reporter.append(project)
    logging.info(f'\033[34m В релизе {release_input} \033[31m{len(fix_issues)}\033[34m задач(-a, -и)\033[0m')
    logging.info(f'\033[34m Из них \033[31m{issue_count}\033[34m задач(-a, -и) с изменениями в статусах выше "Passed QA".\033[0m')
    logging.info(f'\033[34m Изменения в них затронули \033[31m {len(used_projects)} \033[34m проект(-а, '
          f'-ов): \033[31m {", ".join(sorted(projects))}. \033[0m')
    if reporter:
        logging.info('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
        logging.info(f'\033[34m Вам надо получить доступ Developer в проект(-е,'
              f' -ах): \033[31m {", ".join(sorted(reporter))}. \033[0m')
        logging.info('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
    if before_deploy or post_deploy:
        logging.info(f'Есть следующие деплойные действия:')
    for action in chain(before_deploy, post_deploy):
        summary = action[1].replace('# ', '').strip()
        summary = sub('h\d\.', '', summary)
        logging.info(f'\033[31m{action[0]} - \033[0m{summary}')
    if wrong_release_issues:
        logging.info('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
        logging.info(f'\033[34m Следующие задачи не подходят для данного релиза (неправильная страна):\033[0m')
        for issue in sorted(wrong_release_issues):
            logging.info(f'\033[31m {issue}\033[0m')


if __name__ == '__main__':
    main()
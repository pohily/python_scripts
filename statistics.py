# -*- coding: utf-8 -*-

import logging
import os
from itertools import chain

from constants import STATUS_FOR_RELEASE, PROJECTS_COUNTRIES, PROJECTS_NUMBERS, TESTERS
from build import Build

""" Показывает статистику по запрошенному релизу: количество задач, проектов и названия проектов, 
также показываются задачи, которые не подходят для данного релиза (неправильная страна),
задачи без эпика,
Показывает репозитории, к которым необходимо получить доступ для сборки релиза.
Показывает мердж конфликты, если такие есть"""


def main():
    os.makedirs('logs', exist_ok=True)

    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)21s[LINE:%(lineno)3d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)

    build = Build()
    _, release_input, _, fix_issues, _ = build.get_release_details()
    logging.info(f'Статистика релиза {release_input}')
    used_projects = set()
    issue_count = 0
    wrong_release_issues = set()
    country = release_input.split('.')[0].lower()
    before_deploy = []
    post_deploy = []
    without_epic = []
    is_blocked = []
    projects = {}
    for index, issue_number in enumerate(fix_issues):
        # проверка, что задача блокируется
        issue_links = issue_number.fields.issuelinks
        for issue_link in issue_links:
            if issue_link.type.name == 'Blocks':
                try:
                    if issue_link.inwardIssue:
                        is_blocked.append(issue_number.key)
                except AttributeError:
                    pass
            elif issue_link.type.name == 'Gantt End to End' \
                    and issue_link.type.inward == 'has to be finished together with':
                is_blocked.append(issue_number.key)
            elif issue_link.type.name == 'Gantt End to Start' \
                    and issue_link.type.inward == 'has to be done after':
                is_blocked.append(issue_number.key)
        # Проверка того, что у всех задач есть эпик
        if 'сборка' not in issue_number.fields.summary.lower() and not issue_number.fields.customfield_10009:
            without_epic.append(issue_number.key)
        if issue_number.fields.status.name in STATUS_FOR_RELEASE:
            issue_count += 1
            bd = issue_number.fields.customfield_15303  # преддеплойные действия
            if bd:
                before_deploy.append((issue_number.key, bd))
            pd = issue_number.fields.customfield_15302  # постдеплойные действия
            if pd:
                post_deploy.append((issue_number.key, pd))
        else:
            continue
        mr_count = build.get_merge_requests(issue_number=issue_number)
        print(f'{index + 1}) {issue_number} - {issue_number.fields.status.name} - {issue_number.fields.priority.name}:')
        for merge in mr_count:
            if merge.project in projects:
                projects[merge.project] += 1
            else:
                projects[merge.project] = 1
            print(f'    {PROJECTS_NUMBERS[merge.project]} - {projects[merge.project]}')
            status, _, _, _ = build.get_merge_request_details(merge)
            if status != '(/) Нет конфликтов, ':
                logging.exception(f'\033[31m Проверьте мердж реквест {merge.url} в задаче {merge.issue}\033[0m')
            used_projects.add(merge.project)
            try:
                if country not in PROJECTS_COUNTRIES[merge.project].lower():
                    issue = merge.issue.key
                    wrong_release_issues.add(issue)
            except:
                logging.exception(f'У вас нет доступа к проекту {PROJECTS_COUNTRIES[merge.project]}')
    print()
    print(f'\033[34mИтого:\033[0m')
    for project in projects:
        print(f'    {PROJECTS_NUMBERS[project]} - \033[31m{projects[project]}\033[34m \033[0m ('
              f'{ round(projects[project] / (index + 1) * 100)}%)')
    print()
    projects = [PROJECTS_NUMBERS[pr] for pr in used_projects]
    user_id = TESTERS[build.config['user_data']['login']]
    reporter = []
    for project in projects:
        pr = build.gitlab.projects.get(project)
        member = pr.members_all.get(user_id)
        access_level = member.attributes['access_level']
        if access_level < 30:
            reporter.append(project)
    logging.info(f'\033[34m В релизе {release_input} \033[31m{len(fix_issues)}\033[34m задач(-a, -и)\033[0m')
    logging.info(f'\033[34m Из них \033[31m{issue_count}\033[34m задач в статусах выше "Passed QA".\033[0m')
    logging.info(f'\033[34m Изменения в них затронули \033[31m {len(used_projects)} \033[34m проект(-а, '
          f'-ов): \033[36m {", ".join(sorted(projects))}. \033[0m')
    if is_blocked:
        logging.warning('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        logging.info(f'\033[34m Проверить не заблокированы ли задачи: \033[31m '
                     f'{", ".join(sorted(set(is_blocked)))}. \033[0m')
    if without_epic:
        logging.warning('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        logging.info(f'\033[34m Задачи без эпика: \033[31m {", ".join(sorted(without_epic))}. \033[0m')
    if reporter:
        logging.warning('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        logging.info(f'\033[34m Вам надо получить доступ Developer в проект(-е,'
              f' -ах): \033[31m {", ".join(sorted(reporter))}. \033[0m')
        logging.info('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    if before_deploy or post_deploy:
        logging.info(f'\033[34m Есть следующие деплойные действия:\033[0m')
    for action in chain(before_deploy, post_deploy):
        summary = action[1].replace('# ', '').strip()
        # summary = sub('h\d\.', '', summary)
        logging.info(f'\033[31m{action[0]} - \033[0m{summary}')
    if wrong_release_issues:
        logging.warning('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        logging.info(f'\033[34m Следующие задачи не подходят для данного релиза (неправильная страна):\033[0m')
        for issue in sorted(wrong_release_issues):
            logging.info(f'\033[31m {issue}\033[0m')


if __name__ == '__main__':
    main()

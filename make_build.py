# -*- coding: utf-8 -*-

import logging
import os

from build import Build
from constants import RELEASE_URL, ISSUE_URL, DOMAIN


def main():
    os.makedirs('logs', exist_ok=True)
    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)
    logging.info('--------------Начало сборки----------------')

    with open('logs/message.txt', 'w') as file:
        #
        #           Определяем состав релиза
        #
        build = Build()
        _, release_name, _, release_issues, release_id = build.get_release_details()
        #
        #           До таблицы
        #
        message = f"[*Состав релиза:*|{RELEASE_URL.format(DOMAIN, release_id)}]\r\n" \
                  f"||№||Задача||Priority||Мердж реквесты Задача -> RC||Статус реквеста Задача -> RC||\r\n"
        #
        #           Выбираем задачи для релиза в нужных статусах
        #
        logging.info(f'Выбираем задачи для релиза {release_name} в нужных статусах')
        issues_list, before_deploy, post_deploy = build.get_issues_list_and_deploy_actions(release_issues)
        #
        #           Собираем мердж реквесты
        #
        merge_requests, used_projects, MRless_issues_number, message = build.get_mrs_and_used_projects(
            issues_list, message)
        #
        #           Удаляем и создаем RC
        #
        for project in used_projects:
            build.delete_create_rc(project)
        #
        #           Заполняем таблицу
        #
        logging.info('Заполняем таблицу')  # делаем МР в RC и заполняем таблицу ссылками и статусами МР
        for index, issue_number in enumerate(sorted(issues_list)):
            priority = issues_list[issue_number]
            result = build.get_links(issue_number=issue_number, merges=merge_requests[issue_number])
            message += f"|{index + MRless_issues_number}|" \
                       f"[{issue_number}|" \
                       f"{ISSUE_URL}{issue_number}]|" \
                       f"{priority}|{result}\r\n"

        if build.confluence:
            message += f'\n\r[*Отчет о тестировании*.|{build.confluence}]\n\r'
        #
        #           Создаем MR RC -> Staging, RC -> Master для Docker и проектов без стейджинга
        #
        logging.info('------------------------------------------')
        rc_master_links, staging_links = build.make_mr_to_staging(projects=used_projects)
        #
        #           RC -> Staging
        #
        message += '\n\r*RC -> Staging*\r\n'
        for link in staging_links:
            message += f'\n[{link}]\r'
        #
        #           Создаем MR Staging -> Master
        #
        master_links = build.make_mr_to_master(projects=used_projects)
        #
        #           Staging -> Master
        #
        message += '\n\r*Staging -> Master*\r\n'
        for link in master_links:
            message += f'\n[{link}]\r'
        #
        #           Docker и проекты без стейджинга -> Master
        #
        if rc_master_links:
            message += '\r\n*RC -> Master*\r\n'
            for link in rc_master_links:
                message += f'\n[{link}]\r'
        #
        #           Преддеплойные действия
        #
        message_before_deploy = ''
        if before_deploy:
            for issue in before_deploy:
                message_before_deploy += f'* *{issue[0]}*: {issue[1]}\r\n'
        #
        #           Постдеплойные действия
        #
        message_post_deploy = ''
        if post_deploy:
            for issue in post_deploy:
                message_post_deploy += f'* *{issue[0]}*: {issue[1]}\r\n'
        #
        #           Вывод результата в Jira
        #
        CREATE_JIRA_ISSUE = eval(build.config['options']['CREATE_JIRA_ISSUE'])
        if CREATE_JIRA_ISSUE:
            logging.info('Вывод результата в Jira')
            existing_issue = build.jira.search_issues(f'project=SLOV AND summary ~ "Сборка {release_name}"')
            if existing_issue:
                existing_issue = existing_issue[0]
                existing_issue.update(fields={
                    'description': message,
                    'customfield_15303': message_before_deploy,
                    'customfield_15302': message_post_deploy,
                })
            else:
                issue_dict = {
                    "fixVersions": [{"name": release_name, }],
                    'project': {'key': 'SLOV'},
                    'summary': f"Сборка {release_name}",
                    'description': message,
                    'issuetype': {'name': 'RC'},  # специальный тип задачи для сборок
                    'customfield_15303': message_before_deploy,
                    'customfield_15302': message_post_deploy,
                }
                build.jira.create_issue(fields=issue_dict)
        #
        #           Вывод результата в файл
        #
        file.write(message)


if __name__ == '__main__':
    main()


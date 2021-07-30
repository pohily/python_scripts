# -*- coding: utf-8 -*-

import logging
import os
from collections import defaultdict

from constants import PROJECTS_NUMBERS, RELEASE_URL, GIT_LAB, STATUS_FOR_RELEASE, \
    PRIORITY, ISSUE_URL, MR_STATUS
from merge_requests import Build


def get_links(merges, build):
    """ принимает список кортежей МР одной задачи. Делает МР SLOV -> RC.
    Заполняет таблицу ссылками на SLOV -> RC и статусами SLOV -> RC """

    statuses = {}  # предварительно собираем статусы, затем все сразу вписываем в таблицу
    conflict = False  # флаг наличия конфликтов с RC
    for index, merge in enumerate(merges):
        #
        #           Пытаемся создать MR из текущей задачи в RC. Выводим статус в таблицу
        #
        logging.info('------------------------------------------')
        logging.info(f'Пытаемся сделать MR из {merge.issue} в {RC_name} в {PROJECTS_NUMBERS[merge.project]}')

        status, url, mr = build.make_mr_to_rc(merge, RC_name)
        if MR_STATUS['can_be_merged'] not in status:
            logging.warning(f"Конфликт в задаче {merge.issue} в {merge.project}")
            conflict = True

        statuses[index] = [status]  # 0
        statuses[index].append(mr)  # 1
        url_parts = url.split('/')
        # в связи с обновлением gitlab поменялись url 11/03/20:
        if GIT_LAB in url and url_parts[6].isdigit():
            iid = url_parts[6]
        elif GIT_LAB in url and url_parts[7].isdigit():
            iid = url_parts[7]
        else:
            logging.exception(f'Проверьте задачу {issue_number} - некорректная ссылка {url}')
            continue
        statuses[index].append(f'[{url_parts[3]}/{url_parts[4]}/{iid}|{url}]')  # 2
    #
    #           Мержим MR из текущей задачи в RC
    #
    if conflict:
        status = '(x) Не влит'
    else:
        status = '(/) Влит'
    for line in range(len(statuses)):
        if not conflict:
            mr = statuses[line][1]
            status = build.merge_rc(mr)
        statuses[line].append(status)  # 3

    result = ''
    start = True  # флаг первого МР, если их в задаче несколько
    # 0 - статус slov -> RC, 1 - mr, 2 - MR url, 3 - влит/не влит
    for line in range(len(statuses)):
        if not start: # если МР не первый - добавляем перенос на следующую строку и три пустых ячейки
            result += f'\n|  |  |  |'
        result += f'{statuses[line][2]}|{statuses[line][0]}{statuses[line][3]}|'
        start = False
    return result


if __name__ == '__main__':
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
        logging.info('Определяем состав релиза')
        build = Build()
        _, release_name, _, release_issues, release_id = build.get_release_details()
        RC_name = f'rc-{release_name.replace(".", "-")}'
        #
        #           До таблицы
        #
        message = f"[*Состав релиза:*|{RELEASE_URL.format(release_id)}]\r\n" \
                  f"||№||Задача||Приоритет||Мердж реквесты SLOV -> RC||Статус мердж реквеста SLOV -> RC||\r\n"
        #
        #           Выбираем задачи для релиза в нужных статусах
        #
        logging.info(f'Выбираем задачи для релиза {release_name} в нужных статусах')
        issues_list = {}
        before_deploy = []
        post_deploy = []
        for issue in release_issues:
            if 'сборка' not in issue.fields.summary.lower() and issue.fields.status.name in STATUS_FOR_RELEASE:
                issues_list[issue.key] = PRIORITY[issue.fields.priority.name]
                bd = issue.fields.customfield_15303  # переддеплойные действия
                if bd:
                    before_deploy.append((issue.key, bd))
                pd = issue.fields.customfield_15302  # постдеплойные действия
                if pd:
                    post_deploy.append((issue.key, pd))
        #
        #           Собираем мердж реквесты
        #
        logging.info('Собираем мердж реквесты')
        merge_requests = defaultdict(list)  # словарь- задача: список кортежей ссылок и проектов
        used_projects = set()  # сет проектов всего затронутых в релизе
        MRless_issues_number = 1
        MRless_issues = []
        if issues_list:
            for issue_number in issues_list:
                MR_count = build.get_merge_requests(issue_number=issue_number)  # возвращаются только невлитые МР
                if not MR_count: # если в задаче нет МР вносим задачу в таблицу
                    message += f"|{MRless_issues_number}|[{issue_number}|{ISSUE_URL}{issue_number}]|" \
                               f"{issues_list[issue_number]}| Нет изменений |(/)|\r\n"
                    MRless_issues_number += 1
                    MRless_issues.append(issue_number)
                    continue

                issue_projects = set()  # сет проектов всего затронутых в задаче
                for merge in MR_count:
                    used_projects.add(merge.project)
                    if merge.project not in issue_projects:  # проверяем не было ли в этой задаче нескольких МР в одном
                        issue_projects.add(merge.project)    # проекте, если несколько - берем один
                        merge_requests[issue_number].append(merge)

            if MRless_issues:  # убираем задачу без МР из списка задач для сборки RC
                for item in MRless_issues:
                    issues_list.pop(item)
        #
        #           Удаляем и создаем RC
        #
        logging.info('Удаляем и создаем RC')
        for project in used_projects:
            build.delete_create_RC(project, RC_name)
        #
        #           Заполняем таблицу
        #
        logging.info('------------------------------------------')
        logging.info('Заполняем таблицу')  # делаем МР в RC и заполняем таблицу ссылками и статусами МР
        for index, issue_number in enumerate(sorted(issues_list)):
            priority = issues_list[issue_number]
            result = get_links(merge_requests[issue_number], build)
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
        logging.info('Делаем МР RC -> Staging, RC -> Master')
        rc_master_links, staging_links = build.make_mr_to_staging(used_projects, RC_name)
        #
        #           RC -> Staging
        #
        logging.info('Заполняем ссылки на МР RC -> Staging')
        message += '\n\r*RC -> Staging*\r\n'
        for link in staging_links:
            message += f'\n[{link}]\r'
        #
        #           Создаем MR Staging -> Master
        #
        logging.info('Делаем МР Staging -> Master')
        master_links = build.make_mr_to_master(used_projects)
        #
        #           Staging -> Master
        #
        logging.info('Заполняем ссылки на МР Staging -> Master')
        message += '\n\r*Staging -> Master*\r\n'
        for link in master_links:
            message += f'\n[{link}]\r'
        #
        #           Docker и проекты без стейджинга -> Master
        #
        if rc_master_links:
            logging.info('Заполняем ссылки на МР RC -> Master')
            message += '\r\n*RC -> Master*\r\n'
            for link in rc_master_links:
                message += f'\n[{link}]\r'
        #
        #           Преддеплойные действия
        #
        logging.info('Заполняем деплойные действия')
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
                    "fixVersions": [{"name": release_name,}],
                    'project': {'key': 'SLOV'},
                    'summary': f"Сборка {release_name}",
                    'description': message,
                    'issuetype': {'name': 'RC'},  #  специальный тип задачи для сборок
                    'customfield_15303': message_before_deploy,
                    'customfield_15302': message_post_deploy,
                }
                new_issue = build.jira.create_issue(fields=issue_dict)
        #
        #           Вывод результата в файл
        #
        file.write(message)


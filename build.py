import logging
from collections import namedtuple, defaultdict
from configparser import ConfigParser
from datetime import datetime
from sys import argv
from time import sleep

import gitlab
import requests
from atlassian import Confluence
from jira import JIRA

from constants import *


class Build:

    Merge_request = namedtuple('Merge_request',
                               ['url', 'iid', 'project', 'issue'])  # iid - номер МР в url'е, project - int

    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.jira = JIRA(options=JIRA_OPTIONS, auth=(self.config['user_data']['login'],
                                                     self.config['user_data']['jira_password']))
        self.gitlab = gitlab.Gitlab(GIT_LAB_SERVER, private_token=self.config['user_data']['GITLAB_PRIVATE_TOKEN'])
        self.name = self.get_release_name()
        self.rc_name = f'rc-{self.name.replace(".", "-")}'
        self.merge_fail = False                                     # наличие незамерженных МР
        self.docker = False                                         # наличие докера в релизе
        self.confluence = self.confluence_link(self.name)           # ссылка на конфлуенс
        self.merge_request_details = namedtuple(
            'Merge_request_details', ['merge_status', 'source_branch', 'target_branch', 'state']
        )

    def get_issues_list_and_deploy_actions(self, release_issues):
        """ возвращаем  словарь: навание задачи: ее приоритет - для таблички
                        пред- и пост- деплойные действия"""
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
        return issues_list, before_deploy, post_deploy

    def get_mrs_and_used_projects(self, issues_list, message, return_merged=False):
        """
        возвращаем  словарь- задача: список кортежей ссылок и проектов
                    сет проектов всего затронутых в релизе
                    количество задач без реквестов
                    и записывает в табличку задачи без реквестов
        """
        merge_requests = defaultdict(list)  # словарь- задача: список кортежей ссылок и проектов
        used_projects = set()  # сет проектов всего затронутых в релизе
        MRless_issues_number = 1
        MRless_issues = []
        if issues_list:
            for issue_number in issues_list:
                # :return_merged: передается True если надо вернуть влитые МР, обычно возвращаются только невлитые"""
                MR_count = self.get_merge_requests(issue_number=issue_number, return_merged=return_merged)
                if not MR_count:  # если в задаче нет МР вносим задачу в таблицу
                    if message:
                        message += f"|{MRless_issues_number}|[{issue_number}|{ISSUE_URL}{issue_number}]|" \
                                   f"{issues_list[issue_number]}| Нет изменений |(/)|\r\n"
                    MRless_issues_number += 1
                    MRless_issues.append(issue_number)
                    continue

                issue_projects = set()  # сет проектов всего затронутых в задаче
                for merge in MR_count:
                    used_projects.add(merge.project)
                    if merge.project not in issue_projects:  # проверяем не было ли в этой задаче нескольких МР в одном
                        issue_projects.add(merge.project)  # проекте, если несколько - берем один
                        merge_requests[issue_number].append(merge)

            if MRless_issues:  # убираем задачу без МР из списка задач для сборки RC
                for item in MRless_issues:
                    issues_list.pop(item)
            return merge_requests, used_projects, MRless_issues_number, message

    def confluence_link(self, title):
        confluence = Confluence(
            url=CONFLUENCE_SERVER,
            username=self.config['user_data']['login'],
            password=self.config['user_data']['jira_password']
        )
        try:
            link = confluence.get_page_by_title(space='AT', title=f'Релиз {title} Отчет о тестировании')
            return CONFLUENCE_LINK.format(link['id'])
        except (TypeError, IndexError):
            return ''

    def get_release_name(self):
        _, name, _, _, _ = self.get_release_details()
        return name

    def get_release_details(self, date=False, release=False):
        """ Получает имя релиза из командной строки, либо передается аргументом,
            либо в тестовом режиме - HARDCODE_RELEASE из конфига
            Возвращает: дату, имя, страну, задачи релиза и id """

        if not release:
            try:
                COMMAND_LINE_INPUT = eval(self.config['options']['COMMAND_LINE_INPUT'])
                if COMMAND_LINE_INPUT:
                    if argv[1].startswith('-'):
                        if argv[1] in ('-g', '-q'):
                            release_input = argv[2]
                        elif argv[1] in ('-l', '-h', '-e'):
                            release_input = argv[3]
                        else:
                            release_input = argv[2]
                            logging.exception('Неизвестный флаг!')
                    else:
                        release_input = argv[1]
                else:
                    release_input = self.config['options']['hardcode_release']
            except IndexError:
                logging.exception('Введите имя релиза!')
                raise Exception('Введите имя релиза!')
        else:
            release_input = release
        fix_issues = self.jira.search_issues(f'fixVersion={release_input} ORDER BY priority DESC')
        if date:
            try:
                fix_date = fix_issues[0].fields.fixVersions[0].releaseDate
                fix_date = datetime.strptime(fix_date, '%Y-%m-%d').strftime('%d.%m.%Y')
            except (AttributeError, UnboundLocalError, TypeError):
                fix_date = None
                logging.exception(f'Релиз {release_input} еще не выпущен!')
        else:
            fix_date = None
        country = release_input.split('.')[0].lower()
        release_country = COUNTRIES[country]
        fix_id = fix_issues[0].fields.fixVersions[0].id
        return fix_date, release_input, release_country, fix_issues, fix_id

    def get_merge_requests(self, issue_number, return_merged=False) -> list:
        """ Ищет ссылки на МР в задаче и возвращает их список
        :return_merged: передается True если надо вернуть влитые МР, обычно возвращаются только невлитые"""

        result = []
        links_json = requests.get(url=REMOTE_LINK.format(issue_number),
                                  auth=(self.config['user_data']['login'],
                                        self.config['user_data']['jira_password'])).json()
        for link in links_json:
            if 'confluence' in link['object']['url']:
                continue
            if 'commit' in link['object']['url'] or GIT_LAB not in link['object']['url']:
                continue
            # для предупреждения о запуске тесто после сборки контейнеров
            if 'docker' in link['object']['url']:  # or 'msm' in link['object']['url']: - пока убрали - надо вливать в стейджинг
                self.docker = True
            url_parts = link['object']['url'].split('/')
            if len(url_parts) < 6:
                continue
            if 'leasing' in link['object']['url'] and '4slovo.kz' in link['object']['url']:
                # добавился новый тип проектов из трех частей 06.24
                try:
                    project = PROJECTS_NAMES[f'{url_parts[3]}/{url_parts[4]}/{url_parts[5]}']
                except KeyError:
                    logging.exception(
                        f'Проверьте {issue_number} - не найден проект {url_parts[3]}/{url_parts[4]}/{url_parts[5]}')
                    continue
            else:
                try:
                    project = PROJECTS_NAMES[f'{url_parts[3]}/{url_parts[4]}']
                except KeyError:
                    logging.exception(
                        f'Проверьте {issue_number} - не найден проект {url_parts[3]}/{url_parts[4]}')
                    continue
            # в связи с обновлением gitlab поменялись url 11/03/20, добавился новый тип проектов из трех частей 06.24:
            if GIT_LAB in link['object']['url'] and url_parts[6].isdigit():
                iid = url_parts[6]
            elif GIT_LAB in link['object']['url'] and url_parts[7].isdigit():
                iid = url_parts[7]
            elif GIT_LAB in link['object']['url'] and 'leasing' in link['object']['url'] and url_parts[8].isdigit():
                iid = url_parts[8]
            else:
                logging.warning(f"Проверьте ссылку {link['object']['url']} в задаче {issue_number}")
                continue
            merge = self.Merge_request(link['object']['url'], iid, project, issue_number)
            if return_merged:
                result.append(merge)
            else:
                if not self.is_merged(merge):
                    result.append(merge)
        return result

    def get_links(self, issue_number, merges):
        """ принимает номер задачи и список кортежей ее МР.
        Делает МР SLOV -> RC.
        Заполняет таблицу ссылками на SLOV -> RC и статусами SLOV -> RC """

        statuses = {}  # предварительно собираем статусы, затем все сразу вписываем в таблицу
        conflict = False  # флаг наличия конфликтов с RC
        for index, merge in enumerate(merges):
            #
            #           Пытаемся создать MR из текущей задачи в RC. Выводим статус в таблицу
            #
            logging.info('------------------------------------------')
            status, url, mr = self.make_mr_to_rc(mr=merge)
            if MR_STATUS['can_be_merged'] not in status:
                logging.error(f"Конфликт в задаче {merge.issue} в {PROJECTS_NUMBERS[merge.project]}")
                conflict = True

            statuses[index] = [status]  # 0
            statuses[index].append(mr)  # 1
            url_parts = url.split('/')
            # в связи с обновлением gitlab поменялись url 11/03/20:
            leasing = 0
            if GIT_LAB in url and url_parts[6].isdigit():
                iid = url_parts[6]
            elif GIT_LAB in url and url_parts[7].isdigit():
                iid = url_parts[7]
            elif GIT_LAB in url and 'leasing' in url and url_parts[8].isdigit():
                iid = url_parts[8]
                leasing = 1
            else:
                logging.exception(f'Проверьте задачу {issue_number} - некорректная ссылка {url}')
                continue
            if leasing:
                statuses[index].append(f'[{url_parts[3]}/{url_parts[4]}/{url_parts[5]}/{iid}|{url}]')  # 2
            else:
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
                status = self.merge_rc(mr)
            statuses[line].append(status)  # 3

        result = ''
        start = True  # флаг первого МР, если их в задаче несколько
        # 0 - статус slov -> RC, 1 - mr, 2 - MR url, 3 - влит/не влит
        for line in range(len(statuses)):
            if not start:  # если МР не первый - добавляем перенос на следующую строку и три пустых ячейки
                result += f'\n| " | " | " |'
            result += f'{statuses[line][2]}|{statuses[line][0]}{statuses[line][3]}|'
            start = False
        return result

    def delete_create_rc(self, project):
        """ Для каждого затронутого релизом проекта удаляем RC, если есть. Затем создаем RC """
        if TEST:
            return '(/)Тест'

        pr = self.gitlab.projects.get(f'{project}')
        try:
            rc = pr.branches.get(f'{self.rc_name}')
            rc.delete()
            pr.branches.create({'branch': f'{self.rc_name}', 'ref': 'master'})
        except (gitlab.exceptions.GitlabGetError, gitlab.exceptions.GitlabHttpError):
            pr.branches.create({'branch': f'{self.rc_name}', 'ref': 'master'})

    def get_merge_request_details(self, mr):
        """ Возвращает статус (есть или нет конфликты), source_branch, target_branch, state: влит/не влит"""
        _, iid, project, _ = mr
        token = f"private_token={(self.config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
        details = requests.get(url=MR_BY_IID.format(project, iid, token)).json()
        if details:
            details = details[0]
            return self.merge_request_details(
               MR_STATUS[details['has_conflicts']], details['source_branch'], details['target_branch'], details['state']
            )
        else:
            logging.error(f'MR не найден {mr}')
            return self.merge_request_details('MR не найден', '', '', '')

    def is_merged(self, merge) -> bool:
        """ Возвращаем статус МР в мастер """
        pr = self.gitlab.projects.get(f'{merge.project}')
        _, source, _, _ = self.get_merge_request_details(merge)
        mr = pr.mergerequests.list(state='merged', source_branch=source, target_branch='master')
        return bool(mr)

    def make_mr_to_rc(self, mr):
        """ Создаем МР slov -> RC. Возвращаем статус МР, его url и сам МР"""
        if TEST:
            return '(/) Тест', 'https://gitlab.4slovo.ru/4slovo.ru/chestnoe_slovo_backend/merge_requests/тест', 'тест'

        project = self.gitlab.projects.get(f'{mr.project}')
        _, source_branch, target_branch, state = self.get_merge_request_details(mr)
        if state == 'merged' and target_branch == 'master':              # если МР уже влит в мастер - не берем его в RC
            logging.warning(f'В задаче {mr.issue} мердж реквест {mr.project} уже в мастере')
            return '(/) Уже в мастере, ', mr.url, False
        target_branch = f'{self.rc_name}'
        #
        #           проверка статусов pipeline
        #
        status = ''
        if mr.project in PROJECTS_WITH_TESTS:
            issue = mr.issue.lower()
            pipelines = project.pipelines.list(ref=f'{issue}', get_all=True)
            if pipelines:
                pipeline = pipelines[0]
                pipeline_jobs = pipeline.jobs.list()
                pipeline_job = pipeline_jobs[0]
                logging.info(f"pipelines - {[pipeline.attributes['id'] for pipeline in pipelines]}")
                logging.info(f"jobs in {pipeline.attributes['id']} - "
                             f"{[pipeline_job.attributes['id'] for pipeline_job in pipeline_jobs]}")
                logging.info(f"pipeline {pipeline.attributes['id']} "
                             f"job {pipeline_job.attributes['id']} "
                             f"status = '{pipeline_job.attributes['status']}'")
                if pipeline_job.attributes['status'] != 'success':
                    logging.warning(f'В задаче {mr.issue} в проекте {PROJECTS_NUMBERS[mr.project]} не прошли тесты')
                    if mr.project in DOCKER_PROJECTS:
                        status = '(x) Контейнеры не сбилжены!, '
                    else:
                        status = '(x) Тесты не прошли!, '

        merge = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
        if merge:
            merge = merge[0]
        else:
            merge = project.mergerequests.create({'source_branch': source_branch,
                                                  'target_branch': target_branch,
                                                  'title': f"{mr.issue.replace('-', '_')} -> {self.rc_name}",
                                                  'target_project_id': mr.project,
                                                  })
        merge_status, _, _, _ = self.get_merge_request_details(
            (1, merge.attributes['iid'], merge.attributes['project_id'], 1)
        )
        status += merge_status
        url = merge.attributes['web_url']
        return status, url, merge

    def merge_rc(self, mr):
        if TEST:
            return

        if not isinstance(mr, bool) and mr.attributes['state'] != 'merged':
            logging.info(f"Мержим MR {mr.attributes['iid']} merge_status={mr.attributes['merge_status']}, "
                         f"has_conflicts={mr.attributes['has_conflicts']}, из {mr.attributes['source_branch']} в RC")
            try:
                mr.merge()
                logging.info('OK')
                return '(/) Влит'
            except:
                sleep(3)  # 2nd try после обновления Гитлаб бывает не сразу дает статус МР
                try:
                    mr.merge()
                    logging.info('2 Try. OK')
                    return '(/) Влит'
                except:
                    self.merge_fail = True
                    logging.error(f"{mr.attributes['iid']} НЕ ВЛИТ! - Конфликт?")
                    return '(x) Не влит'

    def make_mr_to_staging(self, projects):
        """ Делаем МР из RC в стейджинг для всех затронутых проектов и возвращаем список ссылок на МР """
        if TEST:
            return [projects]

        staging_links = []  # ссылки для вывода под таблицей
        master_links = []
        if self.docker:
            tests = DOCKER_PROJECTS
            logging.warning(
                '\033[31m Запустите тесты в Gitlab после сборки контейнеров докера/msm/финмодуля в RC вручную! \033[0m'
            )
        else:
            tests = PROJECTS_WITH_TESTS
        for pr in projects:
            project = self.gitlab.projects.get(pr)
            source_branch = self.rc_name
            if pr in DOCKER_PROJECTS or pr in PROJECTS_WITHOUT_STAGING:
                target_branch = 'master'
            else:
                target_branch = 'staging'
            title = f'{self.rc_name} -> {target_branch}'
            mr = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
            if mr:
                mr = mr[0]
            else:
                mr = project.mergerequests.create({'source_branch': source_branch,
                                                   'target_branch': target_branch,
                                                   'title': title,
                                                   'target_project_id': pr,
                                                   })
            if pr in DOCKER_PROJECTS or pr in PROJECTS_WITHOUT_STAGING:
                master_links.append(mr.attributes['web_url'])
            else:
                staging_links.append(mr.attributes['web_url'])

            # для 4slovo.ru/api (проект 79) всегда делаем файл last_build - т.к. там билдится образ на его основе
            if MAKE_LAST_BUILD_FILE_AND_START_TESTS or pr == 79:
                # Делаем коммит с названием последнего билда - раньше запускал тесты и билд контейнеров докера,
                # сейчас отключили автоматический запуск тестов - запускаю дальше вручную
                try:
                    project.branches.get(self.rc_name)   # если в проекте нет RC,то и коммит не нужен
                    try:
                        commit_json = {
                            "branch": f"{self.rc_name}",
                            "commit_message": "actualize last_build",
                            "actions": [
                                {
                                    "action": "update",
                                    "file_path": f"last_build",
                                    "content": f"{self.rc_name}"
                                },
                            ]
                        }
                        project.commits.create(commit_json)
                    except gitlab.exceptions.GitlabCreateError:
                        commit_json = {
                            "branch": f"{self.rc_name}",
                            "commit_message": "actualize last_build",
                            "actions": [
                                {
                                    "action": "create",
                                    "file_path": f"last_build",
                                    "content": f"{self.rc_name}"
                                },
                            ]
                        }
                        project.commits.create(commit_json)
                except gitlab.exceptions.GitlabGetError:
                    logging.exception(f'Не найдена ветка {self.rc_name} в {PROJECTS_COUNTRIES[pr]}')

                if pr in tests:
                    if not self.merge_fail:
                        sleep(2)  # ждем пока создастся pipeline, иначе тесты запустятся на предыдущей
                        pipelines = project.pipelines.list(get_all=True)
                        # Запуск тестов в проекте
                        for pipeline in pipelines:
                            if pipeline.attributes['ref'] == self.rc_name and pipeline.attributes['status'] == 'skipped':
                                pipeline_job = pipeline.jobs.list()[0]
                                job = project.jobs.get(pipeline_job.id, lazy=True)
                                job.play()
                                logging.info(f'Тесты запущены в проекте {PROJECTS_NUMBERS[pr]}')
                                break
        return master_links, staging_links

    def make_mr_to_master(self, projects):
        """ Делаем МР из стейджинга в мастер для всех затронутых проектов и возвращаем список ссылок на МР """
        if TEST:
            return [projects]

        mr_links = []  # ссылки для вывода под таблицей
        for pr in projects:
            if pr in DOCKER_PROJECTS or pr in PROJECTS_WITHOUT_STAGING:
                continue
            project = self.gitlab.projects.get(pr)
            mr = project.mergerequests.list(state='opened', source_branch='staging', target_branch='master')
            if mr:
                mr = mr[0]
            else:
                mr = project.mergerequests.create({'source_branch': 'staging',
                                                   'target_branch': 'master',
                                                   'title': 'staging -> master',
                                                   'target_project_id': pr,
                                                   })
            mr_links.append(mr.attributes['web_url'])
        return mr_links


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    jira = JIRA(options=JIRA_OPTIONS, auth=(config['user_data']['login'],
                                                 config['user_data']['jira_password']))
    gitlab = gitlab.Gitlab(GIT_LAB_SERVER, private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    project = gitlab.projects.get(11)
    pipelines = project.pipelines.list()

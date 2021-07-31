import logging
from collections import namedtuple
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
        """ Получает имя релиза из коммандной строки, либо передается агрументом, либо в тестовом режиме - хардкод
            Возвращает: дату, имя, страну, задачи релиза и id """

        if not release:
            try:
                COMMAND_LINE_INPUT = eval(self.config['options']['COMMAND_LINE_INPUT'])
                if COMMAND_LINE_INPUT:
                    release_input = argv[1]
                else:
                    release_input = config['options']['hardcode_release']
            except IndexError:
                logging.exception('Введите имя релиза!')
                raise Exception('Введите имя релиза!')
        else:
            release_input = release
        fix_issues = self.jira.search_issues(f'fixVersion={release_input}')
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
            if 'docker' in link['object']['url'] or 'msm' in link['object']['url']:
                self.docker = True
            url_parts = link['object']['url'].split('/')
            if len(url_parts) < 6:
                continue
            try:
                project = PROJECTS_NAMES[f'{url_parts[3]}/{url_parts[4]}']
            except KeyError:
                logging.exception(f'Проверьте задачу {issue_number} - не найден проект {url_parts[3]}/{url_parts[4]}')
                continue
            # в связи с обновлением gitlab поменялись url 11/03/20:
            if GIT_LAB in link['object']['url'] and url_parts[6].isdigit():
                iid = url_parts[6]
            elif GIT_LAB in link['object']['url'] and url_parts[7].isdigit():
                iid = url_parts[7]
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
        """ принимает номер задачи и список кортежей ее МР. Делает МР SLOV -> RC.
        Заполняет таблицу ссылками на SLOV -> RC и статусами SLOV -> RC """

        statuses = {}  # предварительно собираем статусы, затем все сразу вписываем в таблицу
        conflict = False  # флаг наличия конфликтов с RC
        for index, merge in enumerate(merges):
            #
            #           Пытаемся создать MR из текущей задачи в RC. Выводим статус в таблицу
            #
            logging.info('------------------------------------------')
            logging.info(f'Пытаемся сделать MR из {merge.issue} в {self.rc_name} в {PROJECTS_NUMBERS[merge.project]}')

            status, url, mr = self.make_mr_to_rc(merge)
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
                status = self.merge_rc(mr)
            statuses[line].append(status)  # 3

        result = ''
        start = True  # флаг первого МР, если их в задаче несколько
        # 0 - статус slov -> RC, 1 - mr, 2 - MR url, 3 - влит/не влит
        for line in range(len(statuses)):
            if not start:  # если МР не первый - добавляем перенос на следующую строку и три пустых ячейки
                result += f'\n|  |  |  |'
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
        """ Возвращает статус (есть или нет конфликты), source_branch """
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
        """ Создаем МР slov -> RC. Возвращем статус МР, его url и сам МР"""
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
            pipelines = project.pipelines.list(ref=f'{issue}')
            if pipelines:
                pipelines = pipelines[0]
                if pipelines.attributes['status'] != 'success':
                    logging.warning(f'В задаче {mr.issue} в проекте {PROJECTS_NUMBERS[mr.project]} не прошли тесты')
                    status = '(x) Тесты не прошли!, '

        mr = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
        if mr:
            mr = mr[0]
        else:
            mr = project.mergerequests.create({'source_branch': source_branch,
                                               'target_branch': target_branch,
                                               'title': f"{mr.issue.replace('-', '_')} -> {self.rc_name}",
                                               'target_project_id': mr.project,
                                               })
        merge_status, _, _, _ = self.get_merge_request_details(
            (1, mr.attributes['iid'], mr.attributes['project_id'], 1)
        )
        status += merge_status
        url = mr.attributes['web_url']
        return status, url, mr

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
                sleep(2)  # 2nd try после обновления Гитлаб бывает не сразу дает статус МР
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

            # Делаем коммит с названием последнего билда - раньше запускал тесты и билд контейнеров докера,
            # сейчас отключили автоматический запуск тестов - запускаю дальше вручную
            if pr in tests:
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

                if not self.merge_fail:
                    pipelines = project.pipelines.list()
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

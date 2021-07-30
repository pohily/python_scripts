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

from constants import MR_STATUS, MR_BY_IID, PROJECTS_WITH_TESTS, DOCKER_PROJECTS, PROJECTS_NUMBERS, JIRA_SERVER, \
    PROJECTS_COUNTRIES, TEST, PROJECTS_WITHOUT_STAGING, CONFLUENCE_SERVER, CONFLUENCE_LINK, GIT_LAB_SERVER, COUNTRIES


class Build:

    def __init__(self):
        jira_options = {'server': JIRA_SERVER}
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.jira = JIRA(
            options=jira_options,
            auth=(self.config['user_data']['login'],
                  self.config['user_data']['jira_password'])
        )
        self.name = self.get_release_name()
        self.gl = gitlab.Gitlab(GIT_LAB_SERVER, private_token=self.config['user_data']['GITLAB_PRIVATE_TOKEN'])
        self.merge_fail = False                                     # наличие незамерженных МР
        self.docker = False                                         # наличие докера в релизе
        self.confluence = self.confluence_link(self.name)           # ссылка на конфлуенс
        self.Merge_request_details = namedtuple(
            'Merge_request_details', ['merge_status', 'source_branch', 'target_branch', 'state']
        )

    def confluence_link(self, title):
        confluence = Confluence(
            url=CONFLUENCE_SERVER,
            username=self.config['user_data']['login'],
            password=self.config['user_data']['jira_password']
        )
        link = confluence.get_page_by_title(space='AT', title=f'Релиз {title} Отчет о тестировании')
        return CONFLUENCE_LINK.format(link['id'])

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

    def delete_create_RC(self, project, RC_name):
        """ Для каждого затронутого релизом проекта удаляем RC, если есть. Затем создаем RC """
        if TEST:
            return '(/)Тест'

        pr = self.gl.projects.get(f'{project}')
        try:
            rc = pr.branches.get(f'{RC_name}')
            rc.delete()
            pr.branches.create({'branch': f'{RC_name}', 'ref': 'master'})
        except (gitlab.exceptions.GitlabGetError, gitlab.exceptions.GitlabHttpError):
            pr.branches.create({'branch': f'{RC_name}', 'ref': 'master'})

    def get_merge_request_details(self, MR):
        """ Возвращает статус (есть или нет конфликты), source_branch """
        _, iid, project, _ = MR
        token = f"private_token={(self.config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
        details = requests.get(url=MR_BY_IID.format(project, iid, token)).json()
        if details:
            details = details[0]
            return self.Merge_request_details(
               MR_STATUS[details['has_conflicts']], details['source_branch'], details['target_branch'], details['state']
            )
        else:
            logging.error(f'MR не найден {MR}')
            return self.Merge_request_details('MR не найден', '', '', '')

    def is_merged(self, merge) -> bool:
        """ Возвращаем статус МР в мастер """
        pr = self.gl.projects.get(f'{merge.project}')
        _, source, _, _ = self.get_merge_request_details(merge)
        mr = pr.mergerequests.list(state='merged', source_branch=source, target_branch='master')
        return bool(mr)

    def make_mr_to_rc(self, MR, RC_name):
        """ Создаем МР slov -> RC. Возвращем статус МР, его url и сам МР"""
        if TEST:
            return '(/) Тест', 'https://gitlab.4slovo.ru/4slovo.ru/chestnoe_slovo_backend/merge_requests/тест', 'тест'

        project = self.gl.projects.get(f'{MR.project}')
        _, source_branch, target_branch, state = self.get_merge_request_details(MR)
        if state == 'merged' and target_branch == 'master':              # если МР уже влит в мастер - не берем его в RC
            logging.warning(f'В задаче {MR.issue} мердж реквест {MR.project} уже в мастере')
            return '(/) Уже в мастере, ', MR.url, False
        target_branch = f'{RC_name}'
        #
        #           проверка статусов pipeline
        #
        status = ''
        if MR.project in PROJECTS_WITH_TESTS:
            issue = MR.issue.lower()
            pipelines = project.pipelines.list(ref=f'{issue}')
            if pipelines:
                pipelines = pipelines[0]
                if pipelines.attributes['status'] != 'success':
                    logging.warning(f'В задаче {MR.issue} в проекте {PROJECTS_NUMBERS[MR.project]} не прошли тесты')
                    status = '(x) Тесты не прошли!, '

        mr = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
        if mr:
            mr = mr[0]
        else:
            mr = project.mergerequests.create({'source_branch': source_branch,
                                               'target_branch': target_branch,
                                               'title': f"{(MR.issue).replace('-', '_')} -> {RC_name}",
                                               'target_project_id': MR.project,
                                               })
        merge_status, _, _, _ = self.get_merge_request_details(
            (1, mr.attributes['iid'], mr.attributes['project_id'], 1)
        )
        status += merge_status
        url = mr.attributes['web_url']
        return status, url, mr

    def merge_rc (self, MR):
        if TEST:
            return

        if not isinstance(MR, bool) and MR.attributes['state'] != 'merged':
            logging.info(f"Мержим MR {MR.attributes['iid']} merge_status={MR.attributes['merge_status']}, "
                         f"has_conflicts={MR.attributes['has_conflicts']}, из {MR.attributes['source_branch']} в RC")
            try:
                MR.merge()
                logging.info('OK')
                return '(/) Влит'
            except:
                sleep(2)  # 2nd try
                try:
                    MR.merge()
                    logging.info('2 Try. OK')
                    return '(/) Влит'
                except:
                    self.merge_fail = True
                    logging.error(f"{MR.attributes['iid']} НЕ ВЛИТ! - Конфликт?")
                    return '(x) Не влит'

    def make_mr_to_staging(self, projects, RC_name):
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
            project = self.gl.projects.get(pr)
            source_branch = RC_name
            if pr in DOCKER_PROJECTS or pr in PROJECTS_WITHOUT_STAGING:
                target_branch = 'master'
            else:
                target_branch = 'staging'
            title = f'{RC_name} -> {target_branch}'
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
                    project.branches.get(RC_name)   # если в проекте нет RC,то и коммит не нужен
                    try:
                        commit_json = {
                            "branch": f"{RC_name}",
                            "commit_message": "actualize last_build",
                            "actions": [
                                {
                                    "action": "update",
                                    "file_path": f"last_build",
                                    "content": f"{RC_name}"
                                },
                            ]
                        }
                        project.commits.create(commit_json)
                    except gitlab.exceptions.GitlabCreateError:
                        commit_json = {
                            "branch": f"{RC_name}",
                            "commit_message": "actualize last_build",
                            "actions": [
                                {
                                    "action": "create",
                                    "file_path": f"last_build",
                                    "content": f"{RC_name}"
                                },
                            ]
                        }
                        project.commits.create(commit_json)
                except gitlab.exceptions.GitlabGetError:
                    logging.exception(f'Не найдена ветка {RC_name} в {PROJECTS_COUNTRIES[pr]}')

                if not self.merge_fail:
                    pipelines = project.pipelines.list()
                    # Запуск тестов в проекте
                    for pipeline in pipelines:
                        if pipeline.attributes['ref'] == RC_name and pipeline.attributes['status'] == 'skipped':
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

        mr_links = [] # ссылки для вывода под таблицей
        for pr in projects:
            if pr in DOCKER_PROJECTS or pr in PROJECTS_WITHOUT_STAGING:
                continue
            project = self.gl.projects.get(pr)
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
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    project = gl.projects.get(130)
    mr = project.mergerequests.list(state='merged', target_branch='master')
    pass
    # pipelines = project.pipelines.list()
    # for pipeline in pipelines:
    #     if pipeline.attributes['ref'] == 'rc-ru-6-1-97' and pipeline.attributes['status'] == 'skipped':
    #         pipeline_job = pipeline.jobs.list()[0]
    #         job = project.jobs.get(pipeline_job.id, lazy=True)
    #         job.play()
    #         break

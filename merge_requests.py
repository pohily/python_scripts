import logging
from collections import namedtuple
from configparser import ConfigParser

import gitlab
import requests

TEST = False

PROJECTS_NAMES = {"4slovo.ru/chestnoe_slovo": 7, "4slovo.kz/crm4slovokz": 11, "4slovo.kz/4slovokz": 12,
                  "4slovo.ru/chestnoe_slovo_backend": 20, "4slovo.ru/common": 22, "mrloan.ge/mrloange": 23,
                  "mrloan.ge/crmmrloange": 24, "4slovo.ru/fias": 61, "4slovo.ru/chestnoe_slovo_landing": 62,
                  "4slovo.ru/api": 79, "4slovo/cache": 86, "4slovo/sawmill": 90, "4slovo/common": 91, "4slovo/inn": 92,
                  "4slovo/finance": 93, "docker/finance": 94, "docker/api": 97, "docker/ge": 100,
                  "4slovo/finance_client": 103, "docker/kz": 110, "4slovo/rabbitclient": 113, "4slovo/fs-client": 116,
                  "4slovo/fs": 117, "4slovo/enum-generator": 121, "4slovo/expression": 125, "almal.ge/almalge": 128,
                  "almal.ge/crmalmalge": 129, "4slovo.ru/python-tests": 130, "4slovo/logging": 135,
                  "4slovo/timeservice": 138, "4slovo/timeservice_client": 139, "docker/replicator": 144,
                  "4slovo.ru/python-scripts": 154, "4slovo.kz/landing": 159, "docker/ru": 166, "docker/ru-db": 167,
                  }
MR_STATUS = {'can_be_merged': '(/) Нет конфликтов, ', 'cannot_be_merged': '(x) Конфликт!, '}
PRIORITY = {'Critical': '(!) - Critical', 'Highest': '(*r) - Highest', 'High': '(*) - High', 'Medium': '(*g) - Medium',
            'Low': '(*b) - Low', 'Lowest': '(*b) - Lowest', 'Критический': '(!) - Critical'}

PROJECTS_WITH_TESTS = [11, 20, 79, 110, 166]
DOCKER_PROJECTS = [94, 97, 100, 110, 166, 167]

MR_BY_IID = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?iids[]={}&{}'

Merge_request_details = namedtuple('Merge_request_details', ['merge_status', 'source_branch', 'target_branch', 'state'])


def delete_create_RC(config, project, RC_name):
    """ Для каждого затронутого релизом проекта удаляем RC, если есть. Затем создаем RC """
    if TEST:
        return '(/)Тест'

    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    pr = gl.projects.get(f'{project}')
    try:
        rc = pr.branches.get(f'{RC_name}')
        rc.delete()
        pr.branches.create({'branch': f'{RC_name}', 'ref': 'master'})
    except (gitlab.exceptions.GitlabGetError, gitlab.exceptions.GitlabHttpError):
        pr.branches.create({'branch': f'{RC_name}', 'ref': 'master'})


def get_merge_request_details(config, MR):
    """ Возвращает статус (есть или нет конфликты), source_branch """
    _, iid, project, _ = MR
    token = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
    details = requests.get(url=MR_BY_IID.format(project, iid, token)).json()
    if details:
        details = details[0]
        return Merge_request_details(
            MR_STATUS[details['merge_status']], details['source_branch'], details['target_branch'], details['state']
        )
    else:
        logging.error('MR не найден')
        return Merge_request_details('MR не найден', '', '', '')


def make_mr_to_rc(config, MR, RC_name):
    """ Создаем МР slov -> RC. Возвращем статус МР, его url и сам МР"""
    if TEST:
        return '(/) Тест', 'https://gitlab.4slovo.ru/4slovo.ru/chestnoe_slovo_backend/merge_requests/тест', 'тест'

    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    project = gl.projects.get(f'{MR.project}')

    _, source_branch, target_branch, state = get_merge_request_details(config, MR)
    if state == 'merged' and target_branch == 'master':              # если МР уже влит в мастер - не берем его в RC
        logging.warning(f'В задаче {MR.issue} мердж реквест {MR.project} уже в мастере')
        return '(/) Уже в мастере, ', MR.url, False
    target_branch = f'{RC_name}'
    #
    #           проверка статусов pipeline
    #
    status = ''
    if MR.project in PROJECTS_WITH_TESTS and MR.project != 11:  # пока не проверяем 11 - там они всегда падают
        issue = MR.issue.lower()
        pipelines = project.pipelines.list(ref=f'{issue}')
        if pipelines:
            pipelines = pipelines[0]
            if pipelines.attributes['status'] != 'success':
                logging.warning(f'В задаче {MR.issue} в мердж реквесте {MR.project} уже в не прошли тесты')
                status = '(x) Тесты не прошли!, '

    mr = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
    if mr:
        mr = mr[0]
    else:
        mr = project.mergerequests.create({'source_branch': source_branch,
                                           'target_branch': target_branch,
                                           'title': f"[skip-ci] {(MR.issue).replace('-', '_')} -> {RC_name}",
                                           'target_project_id': MR.project,
                                           })
    status += MR_STATUS[mr.attributes['merge_status']]
    url = mr.attributes['web_url']
    return status, url, mr


def merge_rc (config, MR):
    if TEST:
        return

    gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    if MR.attributes['state'] != 'merged':
        MR.merge()


def make_mr_to_staging(config, projects, RC_name, docker):
    """ Делаем МР из RC в стейджинг для всех затронутых проектов и возвращаем список ссылок на МР """
    if TEST:
        return [projects]

    mr_links = [] # ссылки для вывода под таблицей
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    for pr in projects:
        project = gl.projects.get(pr)
        source_branch = RC_name
        if pr in DOCKER_PROJECTS:
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
        mr_links.append(mr.attributes['web_url'])
        #
        #           Делаем коммит запускающий тесты и билд контейнеров докера, после пропуска этого шага при создании RC
        #
        if docker:
            tests = DOCKER_PROJECTS
            logging.warning('\033[31m Запустите тесты в Gitlab после сборки контейнеров докера в RC вручную! \033[0m')
        else:
            tests = PROJECTS_WITH_TESTS
        if pr in tests:
            try:
                project.branches.get(RC_name)   # если в проетке нет RC,то и коммит не нужен
                try:
                    commit_json = {
                        "branch": f"{RC_name}",
                        "commit_message": "start pipeline commit",
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
                        "commit_message": "start pipeline commit",
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
                pass
    return mr_links


def make_mr_to_master(config, projects):
    """ Делаем МР из стейджинга в мастер для всех затронутых проектов и возвращаем список ссылок на МР """
    if TEST:
        return [projects]

    mr_links = [] # ссылки для вывода под таблицей
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    for pr in projects:
        if pr in DOCKER_PROJECTS:
            continue
        project = gl.projects.get(pr)
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
    for rep in range(170):
        try:
            project = gl.projects.get(rep)
            mr = project.mergerequests.list()
            mr = mr[0]
            mr = mr.attributes['web_url'].split('/')
            print(f'{rep}: "{mr[3]}/{mr[4]}", ')
        except:
            pass

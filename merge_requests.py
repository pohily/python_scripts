from collections import namedtuple
from configparser import ConfigParser

import gitlab
import requests

TEST = False

PROJECTS_NAMES = {"chestnoe_slovo": 7, "crm4slovokz": 11, "4slovokz": 12, "chestnoe_slovo_backend": 20, "common": 91,
                  "chestnoe_slovo_landing": 62, "api": 79, "cache": 86, "sawmill": 90, "inn": 92, "finance": 94,
                  "ge": 100, "robotmailer": 102, "finance_client": 103, "kz": 110, "rabbitclient": 113,
                  "fs-client": 116, "fs": 117, "selenium-chrome": 118, "yaml-config": 119, "money": 120,
                  "enum-generator": 121, "helper": 122, "registry-generator": 123, "interface-generator": 124,
                  "expression": 125, "almalge": 128, "crmalmalge": 129, "python-tests": 130, "logging": 135,
                  "timeservice": 138, "timeservice_client": 139, "consul-swarm": 140, "elk": 141, "replicator": 144,
                  "python-scripts": 154, "landing": 159, "ru": 166, "ru-db": 167, "fias": 61, "mrloange": 23,
                  "crmmrloange": 24,
                  }
MR_STATUS = {'can_be_merged': '(/) Нет конфликтов, ', 'cannot_be_merged': '(x) Конфликт!, '}
PRIORITY = {'Critical': '(!) - Critical', 'Highest': '(*r) - Highest', 'High': '(*) - High', 'Medium': '(*g) - Medium',
            'Low': '(*b) - Low', 'Lowest': '(*b) - Lowest', 'Критический': '(!) - Critical'}
PIPELINE_STATUSES = {'running': 0, 'pending': 0, 'success': 1, 'failed': 0, 'canceled': 0, 'skipped': 0}
PROJECTS_WITH_TESTS = [11, 20, 79, 110, 166]
DOCKER_PROJECTS = [110, 166]

GET_BRANCH = 'https://gitlab.4slovo.ru/api/v4/projects/{}/repository/branches/{}&{}'
MR_BY_IID = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?iids[]={}&{}'
PROJECTS = 'https://gitlab.4slovo.ru/api/v4/projects/{}?{}'

Merge_request_details = namedtuple('Merge_request_details', ['merge_status', 'source_branch', 'target_branch', 'state'])


def delete_create_RC(config, project, RC_name):
    """ Для каждого затронутого релизом проекта удаляем RC, если есть. Затем создаем RC """
    if TEST:
        return '(/)Тест'

    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    pr = gl.projects.get(f'{PROJECTS_NAMES[project]}')
    try:
        rc = pr.branches.get(f'{RC_name}')
        rc.delete()
        pr.branches.create({'branch': f'{RC_name}', 'ref': 'master'})
    except gitlab.GitlabError:
        pr.branches.create({'branch': f'{RC_name}', 'ref': 'master'})


def get_merge_request_details(config, MR):
    """ Возвращает статус (есть или нет конфликты), source_branch """
    _, iid, project, _ = MR
    try:
        project_id = PROJECTS_NAMES[project]
    except KeyError:
        print(f"\033[31m Проверьте МР в задаче {MR.issue} \033[0m")
        return Merge_request_details('MR не найден', '', '', '')
    token = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
    details = requests.get(url=MR_BY_IID.format(project_id, iid, token)).json()
    if details:
        details = details[0]
        return Merge_request_details(
            MR_STATUS[details['merge_status']], details['source_branch'], details['target_branch'], details['state']
        )
    else:
        return Merge_request_details('MR не найден', '', '', '')


def make_rc(config, MR, RC_name):
    """ Создаем МР slov -> RC. Возвращем статус МР, его url и сам МР"""
    if TEST:
        return '(/) Тест', 'https://gitlab.4slovo.ru/4slovo.ru/chestnoe_slovo_backend/merge_requests/тест', 'тест'

    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    project = gl.projects.get(f'{PROJECTS_NAMES[MR.project]}')

    _, source_branch, target_branch, state = get_merge_request_details(config, MR)
    if state == 'merged' and target_branch == 'master':              # если МР уже влит в мастер - не берем его в RC
        return '(/) Уже в мастере', MR.url, False
    target_branch = f'{RC_name}'
    #
    #           проверка статусов pipeline
    #
    status = ''
    if PROJECTS_NAMES[MR.project] in PROJECTS_WITH_TESTS and PROJECTS_NAMES[MR.project] != 11:  # не проверяем 11 - там они всегда падают
        issue = MR.issue.lower()
        pipelines = project.pipelines.list(ref=f'{issue}')
        if pipelines:
            pipelines = pipelines[0]
            if pipelines.attributes['status'] != 'success':
                status = '(x) Тесты не прошли!, '

    mr = project.mergerequests.list(state='opened', source_branch=source_branch, target_branch=target_branch)
    if mr:
        mr = mr[0]
    else:
        mr = project.mergerequests.create({'source_branch': source_branch,
                                           'target_branch': target_branch,
                                           'title': f"[skip-ci] {(MR.issue).replace('-', '_')} -> {RC_name}",
                                           'target_project_id': PROJECTS_NAMES[MR.project],
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
        project = gl.projects.get(PROJECTS_NAMES[pr])
        source_branch = RC_name
        if PROJECTS_NAMES[pr] in (110, 166, 167):    # проекты докера
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
                                               'target_project_id': PROJECTS_NAMES[pr],
                                               })
        mr_links.append(mr.attributes['web_url'])
        #
        #           Делаем коммит запускающий тесты и билд контейнеров докера, после пропуска этого шага при создании RC
        #
        if docker:
            tests = DOCKER_PROJECTS
            print('\033[31m Запустите тесты в Gitlab после сборки контейнеров докера в RC вручную! \033[0m')
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
        if PROJECTS_NAMES[pr] in (110, 166, 167):  # проекты докера
            continue
        project = gl.projects.get(PROJECTS_NAMES[pr])
        mr = project.mergerequests.list(state='opened', source_branch='staging', target_branch='master')
        if mr:
            mr = mr[0]
        else:
            mr = project.mergerequests.create({'source_branch': 'staging',
                                               'target_branch': 'master',
                                               'title': 'staging -> master',
                                               'target_project_id': PROJECTS_NAMES[pr],
                                               })
        mr_links.append(mr.attributes['web_url'])
    return mr_links

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    rc = 'rc-ge-3-7-10'
    project = gl.projects.get(100)
    try:
        branch = project.branches.get(rc)
    except gitlab.exceptions.GitlabGetError:
        pass
    try:
        commit_json = {
            "branch": f"{rc}",
            "commit_message": "start pipeline commit",
            "actions": [
                {
                    "action": "update",
                    "file_path": f"last_build",
                    "content": f"{rc}"
                },
            ]
        }
        commit = project.commits.create(commit_json)
    except gitlab.exceptions.GitlabCreateError:
        commit_json = {
            "branch": f"{rc}",
            "commit_message": "start pipeline commit",
            "actions": [
                {
                    "action": "create",
                    "file_path": f"last_build",
                    "content": f"{rc}"
                },
            ]
        }
        commit = project.commits.create(commit_json)



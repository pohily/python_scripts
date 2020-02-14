from collections import namedtuple
from configparser import ConfigParser

import gitlab
import requests

TEST = False

PROJECTS_NAMES = {"chestnoe_slovo": 7, "crm4slovokz": 11, "4slovokz": 12, "chestnoe_slovo_backend": 20, "common": 91,
                  "chestnoe_slovo_landing": 62, "api": 79, "cache": 86, "sawmill": 90, "inn": 92, "finance": 94,
                  "ge": 100, "robotmailer": 102, "finance_client": 103, "kz": 110, "rabbitClient": 113,
                  "fs-client": 116, "fs": 117, "selenium-chrome": 118, "yaml-config": 119, "money": 120,
                  "enum-generator": 121, "helper": 122, "registry-generator": 123, "interface-generator": 124,
                  "expression": 125, "almalge": 128, "crmalmalge": 129, "python-tests": 130, "logging": 135,
                  "timeservice": 138, "timeservice_client": 139, "consul-swarm": 140, "elk": 141, "Replicator": 144,
                  "python-scripts": 154, "landing": 159, "ru": 166, "ru-db": 167, "fias": 61,
                  }
MR_STATUS = {'can_be_merged': '(/) Нет конфликтов, ', 'cannot_be_merged': '(x) Конфликт!, '}
PRIORITY = {'Critical': '(!) - Critical', 'Highest': '(*r) - Highest', 'High': '(*) - High', 'Medium': '(*g) - Medium',
            'Low': '(*b) - Low', 'Lowest': '(*b) - Lowest', 'Критический': '(!) - Critical'}
PIPELINE_STATUSES = {'running': 0, 'pending': 0, 'success': 1, 'failed': 0, 'canceled': 0, 'skipped': 0}

GET_BRANCH = 'https://gitlab.4slovo.ru/api/v4/projects/{}/repository/branches/{}&{}'
MR_BY_IID = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?iids[]={}&{}'
PROJECTS = 'https://gitlab.4slovo.ru/api/v4/projects/{}?{}'

Merge_request_details = namedtuple('Merge_request_details', ['merge_status', 'source_branch'])


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
    project_id = PROJECTS_NAMES[project]
    token = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
    details = requests.get(url=MR_BY_IID.format(project_id, iid, token)).json()
    if details:
        details = details[0]
        return Merge_request_details(MR_STATUS[details['merge_status']], details['source_branch'])
    else:
        return Merge_request_details('MR не найден', '')


def make_rc(config, MR, RC_name):
    """ Создаем МР slov -> RC. Возвращем статус МР, его url и сам МР"""
    if TEST:
        return '(/) Тест', 'https://gitlab.4slovo.ru/4slovo.ru/chestnoe_slovo_backend/merge_requests/тест', 'тест'

    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    project = gl.projects.get(f'{PROJECTS_NAMES[MR.project]}')

    target_branch = f'{RC_name}'
    _, source_branch = get_merge_request_details(config, MR)
    #
    #           проверка статусов pipeline
    #
    status = ''
    if PROJECTS_NAMES[MR.project] in [20, 79, 110, 166]:  # проекты, в которых есть тесты
        issue = MR.issue.lower()
        pipelines = project.pipelines.list(ref=f'{issue}')
        if pipelines:
            pipelines = pipelines[0]
            if pipelines.attributes['status'] != 'success':
                status = '(x) Тесты не прошли!, '

    mr = project.mergerequests.list(source_branch=source_branch, target_branch=target_branch)
    if mr:
        mr = mr[0]
    else:
        mr = project.mergerequests.create({'source_branch': source_branch,
                                           'target_branch': target_branch,
                                           'title': f"{(MR.issue).replace('-', '_')} -> {RC_name}",
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


def make_mr_to_staging(config, projects, RC_name):
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
        mr = project.mergerequests.list(source_branch=source_branch, target_branch=target_branch)
        if mr:
            mr = mr[0]
        else:
            mr = project.mergerequests.create({'source_branch': source_branch,
                                               'target_branch': target_branch,
                                               'title': title,
                                               'target_project_id': PROJECTS_NAMES[pr],
                                               })
        mr_links.append(mr.attributes['web_url'])
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
    project = gl.projects.get(79)
    mr = project.mergerequests.list(source_branch='slov-4628', target_branch='master')
    pipelines = project.pipelines.list(ref='slov-4628')
    if isinstance(pipelines, list):
        pipelines = pipelines[0]
    status = pipelines.attributes['status']
    if not mr:
        mr = project.mergerequests.create({'source_branch': 'AT-85',
                                           'target_branch': 'master',
                                           'title': f'[skip-ci] test',
                                           'target_project_id': 79,
                                           })
    if isinstance(mr, list):
        mr = mr[0]
    pass



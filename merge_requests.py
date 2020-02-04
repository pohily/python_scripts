from collections import namedtuple
from configparser import ConfigParser
from itertools import chain

import gitlab
import requests

TEST = False

PROJECTS_NAMES = {"chestnoe_slovo": 7, "crm4slovokz": 11, "4slovokz": 12, "chestnoe_slovo_backend": 20, "common": 91,
                  "chestnoe_slovo_landing": 62, "api": 97, "cache": 86, "sawmill": 90, "inn": 92, "finance": 94,
                  "ge": 100, "robotmailer": 102, "finance_client": 103, "kz": 110, "rabbitClient": 113,
                  "fs-client": 116, "fs": 117, "selenium-chrome": 118, "yaml-config": 119, "money": 120,
                  "enum-generator": 121, "helper": 122, "registry-generator": 123, "interface-generator": 124,
                  "expression": 125, "almalge": 128, "crmalmalge": 129, "python-tests": 130, "logging": 135,
                  "timeservice": 138, "timeservice_client": 139, "consul-swarm": 140, "elk": 141, "Replicator": 144,
                  "python-scripts": 154, "landing": 159, "ru": 166, "ru-db": 167,
                  }
MR_STATUS = {'can_be_merged': '(/) Нет конфликтов', 'cannot_be_merged': '(x) Конфликт!'}

MR_BY_TARGET_BRANCH = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?target_branch={}&{}' # не используются
PROJECT_MERGE_REQUESTS = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?{}'

GET_BRANCH = 'https://gitlab.4slovo.ru/api/v4/projects/{}/repository/branches/{}&{}'
MR_BY_IID = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?iids[]={}&{}'
PROJECTS = 'https://gitlab.4slovo.ru/api/v4/projects/{}?{}'

Merge_request_details = namedtuple('Merge_request_details', ['merge_status', 'source_branch'])

projects_with_RC = set() # проекты - int, в которых есть RC
docker_projects_with_RC = set()


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
    """ Создаем RC, если еще нет. Создаем МР slov -> RC. Если нет конфликтов - мерджим МР. Возвращем статус МР """
    if TEST:
        return 'Тест'

    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])

    project = gl.projects.get(f'{PROJECTS_NAMES[MR.project]}')


    try:
        branch = project.branches.get(f'{RC_name}')
    except Exception:
        project.branches.create({'branch': f'{RC_name}', 'ref': 'master'})

    if "docker" in MR.url:
        docker_projects_with_RC.add(MR.project)
    else:
        projects_with_RC.add(MR.project)

    target_branch = f'{RC_name}'
    _, source_branch = get_merge_request_details(config, MR)

    mr = project.mergerequests.create({'source_branch': source_branch,
                                       'target_branch': target_branch,
                                       'title': f'[skip-ci] {MR.issue} -> {RC_name}',
                                       'target_project_id': PROJECTS_NAMES[MR.project],
                                       })
    status = mr.attributes['merge_status']
    if status == 'can_be_merged':
        mr.merge()
    return MR_STATUS[status]


def make_mr_to_staging(config, RC_name):
    ''' Делаем МР из RC в стейджинг и возвращаем список ссылок на МР'''
    if TEST:
        return 'тест'

    mr_links = [] # ссылки для вывода под таблицей
    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])

    for pr in chain(projects_with_RC, docker_projects_with_RC):
        project = gl.projects.get(pr)
        source_branch = RC_name
        if pr in (110, 166, 167):    # проекты докера
            target_branch = 'master'
        else:
            target_branch = 'staging'
        mr = project.mergerequests.create({'source_branch': source_branch,
                                           'target_branch': target_branch,
                                           'title': f'{RC_name} -> {target_branch}',
                                           'target_project_id': pr,
                                           })
        mr_links.append(mr.attributes['web_url'])
    return mr_links


if __name__ == '__main__':

    pass



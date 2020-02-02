import gitlab
from configparser import ConfigParser
import requests
from collections import namedtuple
import json


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

PROJECT_MERGE_REQUESTS = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?{}'
MR_BY_IID = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?iids[]={}&{}'
PROJECTS = 'https://gitlab.4slovo.ru/api/v4/projects/{}?{}'
GET_BRANCH = 'https://gitlab.4slovo.ru/api/v4/projects/{}/repository/branches/{}&{}'

Merge_request_details = namedtuple('Merge_request_details', ['id', 'merge_status', 'source_branch'])

projects_with_RC = set() # проекты, в которых есть RC
docker_projects_with_RC = set()

def get_merge_request_details(config, MR):
    """ Возвращает статус (есть или нет конфликты) и id мердж реквеста (вдруг понадобится) в таблицу """
    _, project, iid = MR
    project_id = PROJECTS_NAMES[project]
    token = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
    details = requests.get(url=MR_BY_IID.format(project_id, iid, token)).json()
    if details:
        details = details[0]
        return Merge_request_details(details['id'], MR_STATUS[details['merge_status']], details['source_branch'])
    else:
        return Merge_request_details('0', 'MR не найден', '')


def make_rc(config, MR, RC_name):
    """ Создаем RC, если еще нет. Создаем МР slov -> RC. Если нет конфликтов - делаем МР. Возвращем статус МР """
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    project = gl.projects.get(f'{PROJECTS_NAMES[MR.project]}')
    if "docker" in MR.url:
        target_branch = project.branches.get('master')
        docker_projects_with_RC.add(PROJECTS_NAMES[MR.project])
    else:
        projects_with_RC.add(PROJECTS_NAMES[MR.project])
        try:
            target_branch = project.branches.get(f'{RC_name}')
        except Exception:
            target_branch = project.branches.create({'branch': f'{RC_name}',
                                                     'ref': 'master'})
    _, _, source = get_merge_request_details(config, MR)
    source_branch = project.branches.get(source)
    mr = project.mergerequests.create({'source_branch': f'{source_branch}',
                                       'target_branch': target_branch,
                                       'title': f'{MR.issue} -> {RC_name}',
                                       'target_project_id': PROJECTS_NAMES[MR.project],
                                       })
    _, status, _ = get_merge_request_details(config, mr)
    if status == 'can_be_merged':
        mr.merge()
    return MR_STATUS[status]
    #return 'Тест'


def get_list_of_RC_projects(project, RC_name):
    result = []
    if project == 'docker':
        source = sorted(docker_projects_with_RC)
    else:
        source = sorted(projects_with_RC)
    for pr in source:
        token = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
        link = requests.get(url=GET_BRANCH.format(PROJECTS_NAMES[pr], RC_name, token))
        result.append(link)
    return sorted(result)


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])

    project = gl.projects.get('130')
    try:
        branch = project.branches.get('rc-ru-5-6-10')
    except Exception:
        print("no")
    pass
    """
    x = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
    projects = {}
    for i in range(200, 300):
        project = requests.get(url=PROJECTS.format(i, x))
        if project.status_code == 200:
            projects[project.json()['name']] = project.json()['id']
    with open('projects.json', 'w') as file:
        json.dump(projects, file)
    pass"""



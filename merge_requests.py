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

Merge_request_details = namedtuple('Merge_request_details', ['id', 'merge_status'])


def get_merge_request_details(config, links):
    """ Возвращает статус (есть или нет конфликты) и id мердж реквеста (вдруг понадобится) в таблицу """
    _, project, iid = links
    project_id = PROJECTS_NAMES[project]
    token = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
    details = requests.get(url=MR_BY_IID.format(project_id, iid, token)).json()
    if details:
        details = details[0]
        return Merge_request_details(details['id'], MR_STATUS[details['merge_status']])
    else:
        return Merge_request_details('0', 'MR не найден')


def make_rc(config, links):
    return 'Тест'


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    """
    projects = gl.projects.list()    
    python_scripts = projects[3]
    branches = python_scripts.branches.list()
    at_85 = branches[0]
    groups = gl.groups.list()
    group = gl.groups.get('3')
    projects = group.projects.list()
    
    x = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
    projects = {}
    for i in range(200, 300):
        project = requests.get(url=PROJECTS.format(i, x))
        if project.status_code == 200:
            projects[project.json()['name']] = project.json()['id']
    with open('projects.json', 'w') as file:
        json.dump(projects, file)
    pass"""



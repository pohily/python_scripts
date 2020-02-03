import gitlab
from configparser import ConfigParser
import requests
from collections import namedtuple

TEST = True

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
MR_BY_TARGET_BRANCH = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?target_branch={}&{}'

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
    if TEST:
        return 'Тест'

    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    project = gl.projects.get(f'{PROJECTS_NAMES[MR.project]}')
    if "docker" in MR.url:
        target_branch = project.branches.get('master')
        docker_projects_with_RC.add(MR.project)
    else:
        projects_with_RC.add(MR.project)
        try:
            target_branch = project.branches.get(f'{RC_name}')
        except Exception:
            target_branch = project.branches.create({'branch': f'{RC_name}',
                                                     'ref': 'master'})
    _, _, source = get_merge_request_details(config, MR)
    source_branch = project.branches.get(source)
    mr = project.mergerequests.create({'source_branch': source_branch,
                                       'target_branch': target_branch,
                                       'title': f'[skip-ci] {MR.issue} -> {RC_name}',
                                       'target_project_id': PROJECTS_NAMES[MR.project],
                                       })
    _, status, _ = get_merge_request_details(config, mr)
    if status == 'can_be_merged':
        mr.merge()
    return MR_STATUS[status]
    #return 'Тест'


def make_mr_to_staging(RC_name, config):
    ''' Делаем МР из RC в стейджинг '''
    if TEST:
        return 'тест'

    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    result = []
    source = sorted(projects_with_RC)
    for pr in source:
        project = gl.projects.get(pr)
        source_branch = project.branches.get(RC_name)
        target_branch = 'staging'
        mr = project.mergerequests.create({'source_branch': source_branch,
                                           'target_branch': target_branch,
                                           'title': f'{RC_name} -> Staging',
                                           'target_project_id': pr,
                                           })
    #todo вывод ссылок в стейджинг

def get_list_of_RC_projects(project, RC_name, config):
    """ Возвращает список ссылок на МР RC -> Staging """
    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    result = []
    if project == 'docker':
        source = sorted(docker_projects_with_RC)
    else:
        source = sorted(projects_with_RC)
    for pr in source:
        project = gl.projects.get(pr)
        branch = project.branches.get(RC_name)
        mr_commit = branch.attributes['commit']['id']
        token = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
        mrs_to_rc = requests.get(url=MR_BY_TARGET_BRANCH.format(pr, RC_name, token)).json()
        for branch in mrs_to_rc:
            if branch['merge_commit_sha'] == mr_commit:
                result.append(branch['web_url'])
                break
    return sorted(result)


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    p = gl.projects.get('166')
    b = p.branches.get('rc-ru-5-6-10')
    mr_commit = b.attributes['commit']['id']
    token = f"private_token={(config['user_data']['GITLAB_PRIVATE_TOKEN'])}"
    mrs_to_rc = requests.get(url=MR_BY_TARGET_BRANCH.format('166', 'rc-ru-5-6-10', token)).json()
    for branch in mrs_to_rc:
        if branch['merge_commit_sha'] == mr_commit:
            url = branch['web_url']
            pass
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



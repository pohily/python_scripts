from configparser import ConfigParser
from datetime import datetime

import paramiko
from jira import JIRA

from build import get_merge_requests
from constants import PROJECTS_NUMBERS, JIRA_SERVER, SYSTEM_USERS, COUNTRIES_ABBR
from send_notifications import get_release_details

""" Показывает статистику по запрошенному релизу: количество задач, проектов и названия проектов, 
также показываются задачи, которые не подходят для данного релиза (неправильная страна).
Показывает репозитории, к которым необходимо получить доступ для сборки релиза.
Показывает мердж конфликты, если такие есть"""


def main():
    config = ConfigParser()
    config.read('config.ini')
    jira_options = {'server': JIRA_SERVER}
    jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
    _, release_input, release_country, fix_issues, _ = get_release_details(config, jira)
    release_country = COUNTRIES_ABBR[release_country]
    used_projects = set()
    for issue_number in fix_issues:
        MR_count = get_merge_requests(config, issue_number)
        for merge in MR_count:
            used_projects.add(merge.project)

    projects = [PROJECTS_NUMBERS[pr] for pr in used_projects]
    system_users = [SYSTEM_USERS[release_country][pr] for pr in projects]
    system_users = [user for user in system_users if user]

    username = config['staging'][f"user_{release_country}"]
    password = config['staging'][f"staging_password_{release_country}"]

    if release_country == 'ru':
        server = 'staging.4slovo.ru'
    else:
        server = 'kz.staging.4slovo.ru'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port=22, username=username, password=password, )

    for user in system_users:
        cmd = f'sudo -Siu {user} tail -50 logs/deploy.log'
        _, ssh_stdout, stderr = client.exec_command(cmd)
        err = stderr.read().decode('utf-8').strip("\n")
        if err:
            print(f'!!!!!!! Error in {user}: {err}')
        else:
            result = ssh_stdout.read().decode('utf-8').strip("\n")
            print(f'{user} ================ Ok. {result}')
    client.close()


if __name__ == '__main__':
    main()
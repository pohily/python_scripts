from configparser import ConfigParser

from jira import JIRA

from build import get_release_details, get_merge_requests
from send_notifications import STATUS_FOR_RELEASE

""" Показывает статистику по запрошенному релизу: количество задач, проетов и названия проектов """

config = ConfigParser()
config.read('config.ini')
jira_options = {'server': 'https://jira.4slovo.ru/'}
jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
release_input, _, fix_issues = get_release_details(config, jira)
used_projects = set()
issue_count = 0
for issue_number in fix_issues:
    MR_count = get_merge_requests(config, issue_number)
    if issue_number.fields.status.name in STATUS_FOR_RELEASE:
        issue_count += 1
    for merge in MR_count:
        used_projects.add(merge.project)
print(f'\033[34m В релизе {release_input} есть изменения в \033[31m {len(used_projects)} \033[34m проектах: \033[31m {", ".join(sorted(used_projects))}.')
print(f'\033[34m Всего \033[31m{issue_count}\033[34m задач в статусах выше "Passed QA". \033[0m')
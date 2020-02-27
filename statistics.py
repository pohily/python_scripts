from configparser import ConfigParser
from itertools import chain
from re import sub

from jira import JIRA

from build import get_release_details, get_merge_requests
from send_notifications import STATUS_FOR_RELEASE

""" Показывает статистику по запрошенному релизу: количество задач, проетов и названия проектов, 
также показываются задачи, которые не подходят для данного релиза (неправильная страна) """

PROJECTS_COUNTRIES = {"chestnoe_slovo": 'ru', "chestnoe_slovo_backend": 'ru',"common": 'ru',
                      "chestnoe_slovo_landing": 'ru', "api": 'ru', "cache": 'ru', "inn": 'ru', "yaml-config": 'ru',
                      "money": 'ru', "enum-generator": 'ru', "interface-generator": 'ru', "expression": 'ru',
                      "logging": 'ru', "timeservice_client": 'ru', "ru": 'ru', "ru-db": 'ru', "helper": 'ru',
                      "registry-generator": 'ru', "finance": 'ru', "fs-client": 'ru', "timeservice": 'ru',
                      "crm4slovokz": "kz", "4slovokz": "kz", "kz": "kz", "landing": 'kz',
                      "sawmill": 'ru, kz',"robotmailer": 'ru, kz', "rabbitсlient": 'ru, kz', "finance_client": 'ru, kz',
                      "fs": 'ru, kz', "ge": "ge", "almalge": "ge", "crmalmalge": "ge", "mrloange": "ge",
                      "crmmrloange": "ge",
                      }

config = ConfigParser()
config.read('config.ini')
jira_options = {'server': 'https://jira.4slovo.ru/'}
jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
#existing_issue = jira.search_issues('key = SLOV-4899')
release_input, _, fix_issues = get_release_details(config, jira)
used_projects = set()
issue_count = 0
wrong_release_issues = set()
country = release_input.split('.')[0].lower()
before_deploy = []
post_deploy = []
for issue_number in fix_issues:
    if issue_number.fields.status.name in STATUS_FOR_RELEASE:
        issue_count += 1
        bd = issue_number.fields.customfield_15303  # переддеплойные действия
        if bd:
            before_deploy.append((issue_number.key, bd))
        pd = issue_number.fields.customfield_15302  # постдеплойные действия
        if pd:
            post_deploy.append((issue_number.key, pd))
    else:
        continue
    MR_count = get_merge_requests(config, issue_number)
    for merge in MR_count:
        used_projects.add(merge.project)
        try:
            if country not in PROJECTS_COUNTRIES[merge.project].lower():
                issue = merge.issue.key
                wrong_release_issues.add(issue)
        except:
            pass
print(f'\033[34m В релизе {release_input} \033[31m{issue_count}\033[34m задач(-a, -и) в статусах выше "Passed QA".')
print(f'\033[34m Изменения в них затронули \033[31m {len(used_projects)} \033[34m проект(-а, -ов): \033[31m {", ".join(sorted(used_projects))}. \033[0m')
if before_deploy or post_deploy:
    print(f'Есть следующие деплойные действия:')
for action in chain(before_deploy, post_deploy):
    summary = action[1].replace('# ', '').strip()
    summary = sub('h\d\.', '', summary)
    print(f'\033[31m{action[0]} - \033[0m{summary}')
if wrong_release_issues:
    print(f'\033[34m Следующие задачи не подходят для данного релиза (неправильная страна):\033[0m')
    for issue in sorted(wrong_release_issues):
        print(f'\033[31m {issue}\033[0m', sep=', ')
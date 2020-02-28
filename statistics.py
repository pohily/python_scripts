from configparser import ConfigParser
from itertools import chain
from re import sub

from jira import JIRA

from build import get_release_details, get_merge_requests
from send_notifications import STATUS_FOR_RELEASE

""" Показывает статистику по запрошенному релизу: количество задач, проетов и названия проектов, 
также показываются задачи, которые не подходят для данного релиза (неправильная страна) """

PROJECTS_COUNTRIES = {"4slovo.ru/chestnoe_slovo": "ru, ", "4slovo.kz/crm4slovokz": "kz, ", "4slovo.kz/4slovokz": "kz, ",
                      "4slovo.ru/chestnoe_slovo_backend": "ru, ", "4slovo.ru/common": "ru, ",
                      "mrloan.ge/mrloange": "ge, ", "mrloan.ge/crmmrloange": "ge, ", "4slovo.ru/fias": "ru, ",
                      "4slovo.ru/chestnoe_slovo_landing": "ru, ", "4slovo.ru/api": "ru, ", "4slovo/cache": "ru, kz, ge",
                      "4slovo/sawmill": "ru, kz, ge", "4slovo/common": "ru, kz, ge", "4slovo/inn": "ru, kz, ge",
                      "4slovo/finance": "ru, kz, ge", "docker/finance": "ru, kz, ge", "docker/api": "ru, kz, ge",
                      "docker/ge": "ge, ", "4slovo/finance_client": "ru, kz, ge", "docker/kz": "kz, ",
                      "4slovo/rabbitclient": "ru, kz, ge", "4slovo/fs-client": "ru, kz, ge", "4slovo/fs": "ru, kz, ge",
                      "4slovo/enum-generator": "ge, ", "4slovo/expression": "ru, kz, ge", "almal.ge/almalge": "ge, ",
                      "almal.ge/crmalmalge": "ge, ", "4slovo.ru/python-tests": "ru, ", "4slovo/logging": "ru, kz, ge",
                      "4slovo/timeservice": "ru, kz, ge", "4slovo/timeservice_client": "ru, kz, ge",
                      "docker/replicator": "ru, kz, ge", "4slovo.ru/python-scripts": "ru, ",
                      "4slovo.kz/landing": "kz, ", "docker/ru": "ru, ", "docker/ru-db": "ru, ",
                      }

config = ConfigParser()
config.read('config.ini')
jira_options = {'server': 'https://jira.4slovo.ru/'}
jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
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
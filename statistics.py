from configparser import ConfigParser

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
                      "sawmill": 'ru, kz',"robotmailer": 'ru, kz', "rabbitClient": 'ru, kz', "finance_client": 'ru, kz',
                      "fs": 'ru, kz', "ge": "ge", "almalge": "ge", "crmalmalge": "ge",
                      }

config = ConfigParser()
config.read('config.ini')
jira_options = {'server': 'https://jira.4slovo.ru/'}
jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
message = 'test'
issue_dict = {
                    "fixVersions": [
                        {
                            "name": 'ru.5.6.20',
                        }
                    ],
                    'project': {'key': 'SLOV'},
                    'summary': f"Сборка ru.5.6.20",
                    'description': message,
                    'issuetype': {'name': 'Задача'},
                    'customfield_15300': 'test before',
                    'customfield_15302': 'test post',
                }
new_issue = jira.create_issue(fields=issue_dict)
release_input, _, fix_issues = get_release_details(config, jira)
used_projects = set()
issue_count = 0
wrong_release_issues = set()
country = release_input.split('.')[0].lower()
for issue_number in fix_issues:
    MR_count = get_merge_requests(config, issue_number)
    if issue_number.fields.status.name in STATUS_FOR_RELEASE:
        issue_count += 1
    for merge in MR_count:
        used_projects.add(merge.project)
        try:
            if country not in PROJECTS_COUNTRIES[merge.project].lower():
                issue = merge.issue.key
                wrong_release_issues.add(issue)
        except:
            pass
print(f'\033[34m В релизе {release_input} есть изменения в \033[31m {len(used_projects)} \033[34m проектах: \033[31m {", ".join(sorted(used_projects))}.')
print(f'\033[34m Всего \033[31m{issue_count}\033[34m задач в статусах выше "Passed QA".')
if wrong_release_issues:
    print(f'\033[34m Следующие задачи не подходят для данного релиза (неправильная страна):\033[0m')
    for issue in sorted(wrong_release_issues):
        print(f'\033[31m {issue}\033[0m' , sep=', ')
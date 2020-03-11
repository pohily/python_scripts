from configparser import ConfigParser
from itertools import chain
from re import sub

import gitlab
from jira import JIRA

from build import get_release_details, get_merge_requests, PROJECTS_NUMBERS
from send_notifications import STATUS_FOR_RELEASE

""" Показывает статистику по запрошенному релизу: количество задач, проетов и названия проектов, 
также показываются задачи, которые не подходят для данного релиза (неправильная страна) """

PROJECTS_COUNTRIES = {7: "ru", 11: "kz", 12: "kz", 20: "ru", 22: "ru", 23: "ge", 24: "ge", 61: "ru",
                      62: "ru", 79: "ru", 86: "ru, kz, ge", 90: "ru, kz, ge", 91: "ru, kz, ge", 92: "ru, kz, ge",
                      93: "ru, kz, ge", 94: "ru, kz, ge", 97: "ru, kz, ge", 100: "ge", 103: "ru, kz, ge", 110: "kz",
                      113: "ru, kz, ge", 116: "ru, kz, ge", 117: "ru, kz, ge", 121: "ge", 125: "ru, kz, ge",
                      128: "ge", 129: "ge", 130: "ru", 135: "ru, kz, ge", 138: "ru, kz, ge", 139: "ru, kz, ge",
                      144: "ru, kz, ge", 154: "ru", 159: "kz", 166: "ru", 167: "ru",
                      }


def main():
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
    projects = [PROJECTS_NUMBERS[pr] for pr in used_projects]
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    user_id = 0
    users = gl.users.list()
    for user in users:
        if user.attributes['username'] == config['user_data']['login']:
            user_id = user.attributes['id']
    reporter = []
    for project in projects:
        pr = gl.projects.get(project)
        member = pr.members.get(user_id)
        access_level = member.attributes['access_level']
        if access_level < 30:
            reporter.append(project)
    print(f'\033[34m В релизе {release_input} \033[31m{issue_count}\033[34m задач(-a, -и) с изменениями в статусах выше "Passed QA".')
    print(f'\033[34m Изменения в них затронули \033[31m {len(used_projects)} \033[34m проект(-а, '
          f'-ов): \033[31m {", ".join(sorted(projects))}. \033[0m')
    if reporter:
        print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
        print(f'\033[34m Вам надо получить доступ Developer в проект(-е,'
              f' -ах): \033[31m {", ".join(sorted(reporter))}. \033[0m')
        print('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
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


if __name__ == '__main__':
    main()
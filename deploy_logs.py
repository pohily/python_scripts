from configparser import ConfigParser

from jira import JIRA

from build import get_merge_requests
from constants import PROJECTS_NUMBERS, JIRA_SERVER
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
    _, release_input, _, fix_issues, _ = get_release_details(config, jira)
    used_projects = set()
    for issue_number in fix_issues:
        MR_count = get_merge_requests(config, issue_number)
        for merge in MR_count:
            used_projects.add(merge.project)

    projects = [PROJECTS_NUMBERS[pr] for pr in used_projects]
    pass


if __name__ == '__main__':
    main()
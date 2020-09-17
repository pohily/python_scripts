import os
from random import choice
from configparser import ConfigParser

from jira import JIRA

from constants import JIRA_SERVER, TESTERS
from send_notifications import get_release_details

""" Переназначает задачи текущего релиза между тестировщиками """


def main():
    os.makedirs('logs', exist_ok=True)
    config = ConfigParser()
    config.read('config.ini')
    jira_options = {'server': JIRA_SERVER}
    jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
    _, release_input, _, fix_issues, _ = get_release_details(config, jira)
    for issue in fix_issues:
        if 'сборка' in issue.fields.summary.lower():
            continue
        assignee = issue.fields.assignee.name
        new_assignee = None
        while not new_assignee:
            candidat = choice(TESTERS)
            if candidat != assignee:
                new_assignee = candidat

        issue.update(fields={
                'assignee': {'name': new_assignee}
            })

if __name__ == '__main__':
    main()
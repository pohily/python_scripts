import os
from configparser import ConfigParser
from random import shuffle

from jira import JIRA

from constants import JIRA_SERVER, TESTERS, STATUS_READY
from send_notifications import get_release_details

""" Переназначает задачи текущего релиза между тестировщиками """


def main():
    os.makedirs('logs', exist_ok=True)
    config = ConfigParser()
    config.read('config.ini')
    jira_options = {'server': JIRA_SERVER}
    jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
    _, release_input, _, fix_issues, _ = get_release_details(config, jira)
    shuffle(TESTERS)
    delta = 0 # treshold for TESTERS in case of issue assign skip
    for index, issue in enumerate(fix_issues):
        if 'сборка' in issue.fields.summary.lower():
            delta += 1
            continue
        if issue.fields.priority.name in STATUS_READY:
            delta += 1
            continue
        new_assignee = TESTERS[(index - delta) % len(TESTERS)]

        issue.update(fields={
                'assignee': {'name': new_assignee}
            })

if __name__ == '__main__':
    main()
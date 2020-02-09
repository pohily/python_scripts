from configparser import ConfigParser

from jira import JIRA

from build import get_release_details, get_merge_requests

config = ConfigParser()
config.read('config.ini')
jira_options = {'server': 'https://jira.4slovo.ru/'}
jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
release_input, _, fix_issues = get_release_details(config, jira)
used_projects = set()
for issue_number in fix_issues:
    MR_count = get_merge_requests(config, issue_number)
    for merge in MR_count:
        used_projects.add(merge.project)
print(f'В релизе {release_input} есть изменения в проектах {", ".join(used_projects)}.')
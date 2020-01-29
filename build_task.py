import configparser
from jira import JIRA

from send_notifications import RELEASE_ISSUES_URL, ISSUE_URL
from send_notifications import get_release_info, get_issues, send_mail

RELEASE_URL = 'https://jira.4slovo.ru/projects/SLOV/versions/{}'


def get_build_task_text(release_info):
    return f"<p>Состав релиза:</p><br><p><a href='{RELEASE_URL.format(release_info['id'])}' " \
           f"class='external-link' rel='nofollow'>{RELEASE_URL.format(release_info['id'])}</a></p>" \
           f"<div class='table-wrap'><table class='confluenceTable'><tbody>"\
           f"<tr><th class='confluenceTh'>№</th><th class='confluenceTh'>Задача</th>" \
           f"<th class='confluenceTh'>Подлит свежий мастер, нет конфликтов</th></tr>"


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    release_info = {}
    release_info['date'], release_info['name'], release_info['country'], release_info['id'] = get_release_info(config)
    issues_of_release_link = RELEASE_ISSUES_URL.format(release_info['name'])
    issues_list = {}
    message = get_build_task_text(release_info)
    for issue in get_issues(config, issues_of_release_link):
        if 'сборка' not in issue['fields']['summary'].lower():
            issues_list[issue['key']] = issue['fields']['summary']

    if issues_list:
        for number, issue_number in enumerate(sorted(issues_list)):
            message += f"<tr><td class='confluenceTd'>{number + 1}</td>" \
                       f"<td class='confluenceTd'><a href='{ISSUE_URL}{issue_number}" \
                       f"'title='{issues_list[issue_number]}' class='issue-link' data-issue-key='{issue_number}'" \
                       f">{issue_number}</a></td><td class='confluenceTd'></td></tr>"

        message += '</tbody></table></div><p></p><p><b>RC -&gt; Staging</b></p>' \
                   '<p></p><p></p><p></p><p></p><p><b>Staging -&gt; Master</b></p><p></p>'
        if release_info['country'] == 'Россия':
            country_key = 'ru'
        elif release_info['country'] == 'Казахстан':
            country_key = 'kz'
        elif release_info['country'] == 'Грузия':
            country_key = 'ge'
        else:
            raise Exception('Страна для релиза не определена')
        release_info['country_key'] = country_key
        send_mail(release_info, message, config)


import sqlite3
from _datetime import datetime
from configparser import ConfigParser

import gitlab
from jira import JIRA

from constants import JIRA_SERVER, TESTERS


def main(month):
    with sqlite3.connect(f'game{datetime.now().strftime("%y")}{month}{datetime.now().strftime("%d")}.db') as connection:
        cursor = connection.cursor()
        cursor.execute("create table data ("
                       "_id integer primary key autoincrement, "
                       "issue text not null, "
                       "release text,"
                       "release_date text not null, "
                       "creator text, "
                       "tester_name text not null,"
                       "action text, "
                       "creation_point numeric default 0, "
                       "testing_point numeric default 0,  "
                       "bonus_point numeric default 1, "
                       "fine_point numeric default 1,"
                       "review_point numeric default 0,"
                       "regress_point numeric default 0)")
        config = ConfigParser()
        config.read('config.ini')
        jira_options = {'server': JIRA_SERVER}
        jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
        start = f'{datetime.now().strftime("%Y")}-{month}-01'
        finish = f'{datetime.now().strftime("%Y")}-{month+1}-01'
        issues = jira.search_issues(
            f'status = "Released to production" and updated >= "{start}" and updated < "{finish}"'
        )
        delta = 0
        for index, issue in enumerate(issues):
            index = index - delta
            releasedate = datetime.strptime(issue.fields.fixVersions[0].releaseDate, '%Y-%m-%d')
            if datetime.strptime(start, '%Y-%m-%d') > releasedate or releasedate > datetime.strptime(finish, '%Y-%m-%d'):
                delta += 1
                continue
            if issue.fields.creator.name in TESTERS:
                creator = issue.fields.creator.displayName
            else:
                creator = ''
            query = f"insert into data values (" \
                    f"{index + 1}," \
                    f"'{issue.key}'," \
                    f"'{issue.fields.fixVersions[0].name}'," \
                    f"'{issue.fields.fixVersions[0].releaseDate}'," \
                    f"'{creator}'," \
                    f"'{issue.fields.assignee.displayName}'," \
                    f"'стейджинг'," \
                    f"'', '', '', '', '', '')"
            cursor.execute(query)
            index += 1
        # вносим данные по влитым задачам AT
        gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
        project = gl.projects.get(130)
        mrs = project.mergerequests.list(state='merged', target_branch='master')
        for mr in mrs:
            if datetime.strptime(mr.attributes['merged_at'].split('T')[0], '%Y-%m-%d').month == month:
                for action in ['создание', 'разработка', 'ревью']:
                    query = f"insert into data values (" \
                            f"{index + 1}," \
                            f"'{mr.attributes['source_branch']}'," \
                            f"''," \
                            f"'{mr.attributes['merged_at'].split('T')[0]}'," \
                            f"'','', '{action}', '', '', '', '', '', '')"
                    cursor.execute(query)
                    index += 1
            else:
                break
        connection.commit()


if __name__ == '__main__':
    month = 5
    main(month)


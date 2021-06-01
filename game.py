import datetime
import sqlite3
from configparser import ConfigParser

import gitlab
from jira import JIRA

from constants import JIRA_SERVER, TESTERS


def main(month):
    with sqlite3.connect(f'game{datetime.datetime.now().strftime("%y%m%d")}-{month}.db') as connection:
        cursor = connection.cursor()
        cursor.execute("create table data ("
                       "id integer primary key autoincrement, "
                       "issue text not null, "
                       "release_name text,"
                       "release_date text not null, "
                       "tester_name text not null,"
                       "action text, "
                       "creation_point numeric default 0, "
                       "testing_point numeric default 0,  "
                       "bonus_point numeric default 1, "
                       "fine_point numeric default 1,"
                       "review_point numeric default 0,"
                       "regress_point numeric default 0,"
                       "development_point numeric default 0)")
        config = ConfigParser()
        config.read('config.ini')
        jira_options = {'server': JIRA_SERVER}
        jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))
        start = f'{datetime.datetime.now().strftime("%Y")}-{month}-01'
        date = datetime.datetime.strptime(start, '%Y-%m-%d')
        finish = datetime.datetime.strptime(f'{datetime.datetime.now().strftime("%Y")}-{month + 1}-01', '%Y-%m-%d')
        # сперва ищем названия всех зарелиженных релизов
        fixes = set()
        while date < finish:
            next_day = date + datetime.timedelta(days=1)
            tmp = jira.search_issues(
                f'status = "Released to production" and resolved >= "{date.strftime("%Y-%m-%d")}" '
                f'and resolved < "{next_day.strftime("%Y-%m-%d")}"'
            )
            if tmp:
                for i in tmp:
                    fixes.add(i.fields.fixVersions[0].name)
            date = next_day
        # теперь ищем все задачи из найденных релизов
        issues = []
        for fix in fixes:
            issues += jira.search_issues(f'fixVersion={fix}')
        # заполняем БД задачами SLOV
        index = 0
        for issue in issues:
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
                    f"''," \
                    f"'', '', '1', '1', '', '', '')"
            cursor.execute(query)
            index += 1
        # вносим данные по влитым задачам AT
        gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
        project = gl.projects.get(130)
        mrs = project.mergerequests.list(state='merged', target_branch='master')
        for mr in mrs:
            if datetime.datetime.strptime(mr.attributes['merged_at'].split('T')[0], '%Y-%m-%d').month == month:
                for action in ['создание', 'разработка', 'ревью']:
                    if action == 'разработка':
                        creator = mr.attributes['author']['name']
                    else:
                        creator = ''
                    query = f"insert into data values (" \
                            f"{index + 1}," \
                            f"'{mr.attributes['source_branch']}'," \
                            f"''," \
                            f"'{mr.attributes['merged_at'].split('T')[0]}'," \
                            f"'{creator}'," \
                            f"'{action}'," \
                            f"'', '', '1', '1', '', '', '')"
                    cursor.execute(query)
                    index += 1
            else:
                continue
        connection.commit()


if __name__ == '__main__':
    month = 5
    main(month)

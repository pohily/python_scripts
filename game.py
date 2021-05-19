from _datetime import datetime
import sqlite3
from configparser import ConfigParser

from jira import JIRA

from constants import JIRA_SERVER, TESTERS


def main(month):
    connection = sqlite3.connect(f'game{datetime.now().strftime("%y")}{month}{datetime.now().strftime("%d")}.db')
    cursor = connection.cursor()
    cursor.execute("create table data ("
                   "_id integer primary key autoincrement, "
                   "issue text not null, "
                   "release text not null,"
                   "release_date text not null, "
                   "creator text, "
                   "tester_name text not null, "
                   "creation_point numeric default 0, "
                   "testing_point numeric default 0,  "
                   "bonus_point numeric default 1, "
                   "fine_point numeric default 1)")
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
                f"'', '', '', '')"
        cursor.execute(query)
    connection.commit()
    connection.close()


if __name__ == '__main__':
    month = 3
    main(month)


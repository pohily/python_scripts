import datetime
from configparser import ConfigParser

import gitlab
from jira import JIRA

from constants import JIRA_SERVER, TESTERS


def csv(month):
    with open(f'game{datetime.datetime.now().strftime("%y%m%d")}-{month}.csv', 'a') as file:
        file.write("id, issue,release_name,release_date,tester_name,action,creation_point,testing_point,bonus_point,"
                   "fine_point,review_point,regress_point,development_point\n")
        config = ConfigParser()
        config.read('config.ini')
        jira_options = {'server': JIRA_SERVER}
        jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))

        if 0 < month < 12:
            start = f'{datetime.datetime.now().strftime("%Y")}-{month}-01'
            finish = datetime.datetime.strptime(f'{datetime.datetime.now().strftime("%Y")}-{month + 1}-01', '%Y-%m-%d')
        elif month == 12:
            start = f'{str(int(datetime.datetime.now().strftime("%Y")) - 1)}-{month}-01'
            finish = datetime.datetime.strptime(f'{datetime.datetime.now().strftime("%Y")}-01-01', '%Y-%m-%d')
        else:
            raise Exception('Некорректный месяц')
        date = datetime.datetime.strptime(start, '%Y-%m-%d')
        # сперва ищем названия всех зарелиженных релизов
        fixes = set()
        cls_issues = set()
        sd_issues = set()
        while date < finish:
            next_day = date + datetime.timedelta(days=1)
            slov = jira.search_issues(
                f'status = "Released to production" and resolved >= "{date.strftime("%Y-%m-%d")}" '
                f'and resolved < "{next_day.strftime("%Y-%m-%d")}"'
            )
            if slov:
                for i in slov:
                    try:
                        fixes.add(i.fields.fixVersions[0].name)
                    except IndexError:
                        pass
            # поддержка
            cls_query = f'project = "Клиентская поддержка" AND created >= "{date.strftime("%Y-%m-%d")}" and ' \
                        f'created < "{next_day.strftime("%Y-%m-%d")}"'
            cls = jira.search_issues(cls_query)
            if cls:
                for issue in cls:
                    try:
                        if issue.fields.assignee.name in TESTERS:
                            cls_issues.add((issue, issue.fields.assignee.name))
                            continue
                        for comment in issue.fields.comment.comments:
                            if comment.author.name in TESTERS:
                                cls_issues.add((issue, comment.author.name))
                                continue
                    except AttributeError:
                        pass
            # Servicedesk
            sd_query = f'"Epic Link" = BA-2362  and status = Closed AND created >= "{date.strftime("%Y-%m-%d")}" and' \
                       f' created < "{next_day.strftime("%Y-%m-%d")}"'
            cls = jira.search_issues(sd_query)
            if cls:
                for issue in cls:
                    try:
                        for comment in issue.fields.comment.comments:
                            if comment.author.name in TESTERS:
                                sd_issues.add((issue, comment.author.name))
                                continue
                    except AttributeError:
                        pass
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
            query = f"{index + 1}," \
                    f"{issue.key}," \
                    f"{issue.fields.fixVersions[0].name}," \
                    f"{issue.fields.fixVersions[0].releaseDate}," \
                    f"{creator},,,,1,1,,,\n"
            file.write(query)
            index += 1
        # вносим данные по влитым задачам AT
        gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
        project = gl.projects.get(130)
        mrs = project.mergerequests.list(state='merged', target_branch='master', get_all=True)
        mrs = [mr for mr in mrs if datetime.datetime.strptime(mr.attributes['merged_at'].split('T')[0], '%Y-%m-%d').month == month]
        if len(mrs) == 20:
            print('Возможно учтены не все задачи AT - проверить!')
        for mr in mrs:
            for action in ['разработка', 'ревью']:
                if action == 'разработка':
                    creator = mr.attributes['author']['name']
                else:
                    creator = 'Михаил А. Похилый'
                query = f"{index + 1}," \
                        f"{mr.attributes['source_branch']},," \
                        f"{mr.attributes['merged_at'].split('T')[0]}," \
                        f"{creator}," \
                        f"{action},,,1,1,,,\n"
                file.write(query)
                index += 1
        # cls and service_desk issues
        support_issues = list(cls_issues) + list(sd_issues)
        for issue in support_issues:
            create_ts = datetime.datetime.strptime(
                issue[0].fields.created.split('T')[0], '%Y-%m-%d').strftime('%Y-%m-%d')
            query = f"{index + 1},{issue[0].key},,{create_ts},{issue[1]},поддержка,,1,1,1,,,\n"
            file.write(query)
            index += 1


if __name__ == '__main__':
    """ Геймификация - https://confluence.4slovo.ru/pages/viewpage.action?pageId=77201416 """
    month = 11
    csv(month)

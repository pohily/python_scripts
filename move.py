import logging
from configparser import ConfigParser
from sys import argv

from jira import JIRA

from constants import JIRA_SERVER, STATUS_FOR_RELEASE
from send_notifications import get_release_details


def main():
    config = ConfigParser()
    config.read('config.ini')
    level = logging.INFO
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)
    jira_options = {'server': JIRA_SERVER}
    jira = JIRA(options=jira_options, auth=(config['user_data']['login'], config['user_data']['jira_password']))

    try:
        if not argv[1].startswith('-'):
            source = argv[1]
            target = argv[2]
        else:
            command = argv[1]
            source = argv[2]
            target = argv[3]
    except IndexError:
        logging.exception('Введите релиз-источник и релиз-назначение!')
        raise Exception('Введите релиз-источник и релиз-назначение!!')

    #
    #           Выбираем задачи для релиза в нужных статусах
    #
    _, _, _, release_issues, _ = get_release_details(config, jira)
    logging.info(f'Выбираем неготовые задачи из релиза {source}')
    for_move = []
    for issue in release_issues:
        if 'сборка' not in issue.fields.summary.lower() and issue.fields.status.name not in STATUS_FOR_RELEASE:
            for_move.append(issue)
            print(issue)


if __name__ == '__main__':
    main()

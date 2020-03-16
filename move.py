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

    # -h, --help - показывается помощь:         python move.py -h
    # без флага - переносятся все задачи в статусах неподходящих для релиза:    python move.py ru.1.2.3 ru.1.3.0
    # -a - переносятся все задачи:              python move.py -a ru.1.2.3 ru.1.3.0
    # -s - переносятся только выбранные задачи: python move.py -s ru.1.2.3 ru.1.3.0 1236, 2356, 1212
    # -e - переносятся все кроме выбранных:     python move.py -e ru.1.2.3 ru.1.3.0 1236, 2356, 1212
    # -r - все задачи переводятся в статус Released to production:              python move.py -r ru.1.2.3
    # (todo и релиз в статус Выпущен)

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

    # проверка на совпадение страны
    if source.split('.')[0] != target.split('.')[0]:
        logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
        raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')
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

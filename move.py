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

    # без флага - переносятся все задачи в статусах неподходящих для релиза:    python move.py ru.1.2.3 ru.1.3.0
    # -h, --help - показывается помощь:                                         python move.py -h
    # -a - переносятся все задачи:                                              python move.py -a ru.1.2.3 ru.1.3.0
    # -s - переносятся только выбранные задачи:                     python move.py -s ru.1.2.3 ru.1.3.0 1236, 2356, 1212
    # -e - переносятся все кроме выбранных:                         python move.py -e ru.1.2.3 ru.1.3.0 1236, 2356, 1212
    # -r - все задачи переводятся в статус Released to production, релиз в статус Выпущен:    python move.py -r ru.1.2.3

    def is_country_ok(source, target):
        # проверка на совпадение страны
        if source.split('.')[0] != target.split('.')[0]:
            return False
        else:
            return True

    def move_bad(source, target):
        if is_country_ok(source, target):
            #  Выбираем задачи для релиза в нужных статусах
            _, _, _, release_issues, _ = get_release_details(config, jira)
            logging.info(f'Выбираем неготовые задачи из релиза {source}')
            for_move = []
            for issue in release_issues:
                if 'сборка' not in issue.fields.summary.lower() and issue.fields.status.name not in STATUS_FOR_RELEASE:
                    for_move.append(issue)
                    print(issue)
        else:
            logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
            raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')

    def move_all(source, target):
        pass

    def move_selected(source, target, issues):
        pass

    def move_except(source, target, issues):
        pass

    def release(source):
        pass

    try:
        if not argv[1].startswith('-'):
            source = argv[1]
            target = argv[2]
            move_bad(source, target)
        else:
            if argv[1] == '-h' or argv[1] == '--help':
                pass
            elif argv[1] == '-a':
                source = argv[2]
                target = argv[3]
                move_all(source, target)
            elif argv[1] == '-s':
                source = argv[2]
                target = argv[3]
                issues = argv[4:]
                move_selected(source, target, issues)
            elif argv[1] == '-e':
                source = argv[2]
                target = argv[3]
                issues = argv[4:]
                move_except(source, target, issues)
            elif argv[1] == '-r':
                source = argv[2]
                release(source)
            else:
                logging.exception('Неизвестная команда!')
                raise Exception('Неизвестная команда!')
    except IndexError:
        logging.exception('Введите релиз-источник и релиз-назначение!')
        raise Exception('Введите релиз-источник и релиз-назначение!!')


if __name__ == '__main__':
    main()

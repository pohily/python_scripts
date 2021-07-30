import logging
import os
from datetime import datetime
from sys import argv

from constants import STATUS_FOR_RELEASE, STATUS_READY
from build import Build


def main():
    build = Build()
    level = logging.DEBUG
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)


    # без флага - переносятся все задачи в статусах неподходящих для релиза:    python move.py ru.1.2.3 ru.1.3.0
    # -g - переносятся задачи в подходящих для релиза статусах                  python move.py -g ru.1.2.3 ru.1.3.0
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
            _, _, _, release_issues, _ = build.get_release_details()
            logging.info(f'Выбираем неготовые задачи из релиза {source}')
            for_move = []
            for issue in release_issues:
                if 'сборка' not in issue.fields.summary.lower() and issue.fields.status.name not in STATUS_FOR_RELEASE:
                    for_move.append(issue)
            logging.info(f'Найдено {len(for_move)} неготовых задач(-и, -а)')
            logging.info(f'Переносим неготовые задачи в релиз {target}')
            for issue in for_move:
                logging.info(f'Переносим задачу {issue}')
                issue.update(fields={
                    "fixVersions": [{"name": target, }]
                })
            logging.info(f'Перенос выполнен')
        else:
            logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
            raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')

    def move_good(source, target):
        if is_country_ok(source, target):
            _, _, _, release_issues, _ = build.get_release_details(release=source)
            logging.info(f'Выбираем готовые задачи из релиза {source}')
            for_move = []
            for issue in release_issues:
                if 'сборка' not in issue.fields.summary.lower() and issue.fields.status.name in STATUS_FOR_RELEASE:
                    for_move.append(issue)
            logging.info(f'Найдено {len(for_move)} готовых задач(-и, -а)')
            logging.info(f'Переносим готовые задачи в релиз {target}')
            for issue in for_move:
                logging.info(f'Переносим задачу {issue}')
                issue.update(fields={
                    "fixVersions": [{"name": target, }]
                })
            logging.info(f'Перенос выполнен')
        else:
            logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
            raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')

    def move_all(source, target):
        logging.exception('Пока не реализовано!')

    def move_selected(source, target, issues):
        # not implemented
        if not issues:
            logging.exception('Введите номера задач для переноса!')
        else:
            if is_country_ok(source, target):
                _, _, _, release_issues, _ = build.get_release_details(release=source)
                for issue in issues:
                    if issue.isdigit():
                        issue = f'SLOV-{issue}'
                    else:
                        issue = issue.upper()
                for issue in release_issues:
                    if issue.key in issues:
                        logging.info(f'Переносим задачу {issue}')
                        issue.update(fields={
                            "fixVersions": [{"name": target, }]
                        })
                    else:
                        logging.exception(f'Задача {issue} в релизе {source} не найдена')
                logging.info(f'Перенос выполнен')
            else:
                logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
                raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')

    def move_except(source, target, issues):
        logging.exception('Пока не реализовано!')

    def release(source):
        _, _, _, release_issues, _ = build.get_release_details(release=source)
        for issue in release_issues:
            today = datetime.today().strftime('%Y-%m-%d')
            if issue.fields.status.name in STATUS_READY:
                logging.info(f'Релизим задачу {issue}')
                transitions = build.jira.transitions(issue)
                transitions_ids = [(t['id'], t['name']) for t in transitions]
                id = ''
                for transition in transitions_ids:
                    if transition[1] == 'Release to Production':
                        id = transition[0]
                        break
                if id:
                    build.jira.transition_issue(issue, id)
                    issue.update(fields={"fixVersions": {"released": True, "releaseDate": today}})
                else:
                    logging.exception(f'Задача {issue} еще не переведена в статус подходящий для релиза!')
            else:
                logging.exception(f'Задача {issue} еще не переведена в статус подходящий для релиза!')
        logging.info(f'Релиз и все входящие в него задачи переведены в статус Released to production')

    #
    # Получаем данные из коммандной строки
    #
    if not os.path.exists('logs'):
        os.mkdir(os.getcwd() + '/log')
    try:
        COMMAND_LINE_INPUT = eval(build.config['options']['COMMAND_LINE_INPUT'])
        if COMMAND_LINE_INPUT:
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
                elif argv[1] == '-g':
                    source = argv[2]
                    target = argv[3]
                    move_good(source, target)
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
        else:
            logging.exception('Работает только с командной строкой!')
            raise Exception('Работает только с командной строкой!')
    except IndexError:
        logging.exception('Введите релиз-источник и релиз-назначение!')
        raise Exception('Введите релиз-источник и релиз-назначение!!')


if __name__ == '__main__':
    main()

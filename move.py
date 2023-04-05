import logging
import os
from sys import argv

from constants import STATUS_FOR_RELEASE, STATUS_FOR_QA, PRIORITY_VALUE
from build import Build


def main():
    """
    без флага - переносятся все задачи в статусах неподходящих для релиза:    python move.py ru.1.2.3 ru.1.3.0
    -g - переносятся задачи в подходящих для релиза статусах                  python move.py -g ru.1.2.3 ru.1.3.0
    -q - переносятся задачи в подходящих для тестирования статусах            python move.py -q ru.1.2.3 ru.1.3.0
    """
    build = Build()
    level = logging.DEBUG
    handlers = [logging.FileHandler('logs/log.txt'), logging.StreamHandler()]
    format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
    logging.basicConfig(level=level, format=format, handlers=handlers)

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
                logging.info(f'Переносим задачу {issue}, {issue.fields.status.name}')
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
                logging.info(f'Переносим задачу {issue}, {issue.fields.status.name}')
                issue.update(fields={
                    "fixVersions": [{"name": target, }]
                })
            logging.info(f'Перенос выполнен')
        else:
            logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
            raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')

    def move_qa(source, target):
        if is_country_ok(source, target):
            _, _, _, release_issues, _ = build.get_release_details(release=source)
            logging.info(f'Выбираем готовые для тестирования задачи из релиза {source}')
            for_move = []
            for issue in release_issues:
                if 'сборка' not in issue.fields.summary.lower() and issue.fields.status.name in STATUS_FOR_QA:
                    for_move.append(issue)
            logging.info(f'Найдено {len(for_move)} готовых для тестирования задач(-и, -а)')
            logging.info(f'Переносим готовые для тестирования задачи в релиз {target}')
            for issue in for_move:
                logging.info(f'Переносим задачу {issue}, {issue.fields.status.name}')
                issue.update(fields={
                    "fixVersions": [{"name": target, }]
                })
            logging.info(f'Перенос выполнен')
        else:
            logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
            raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')

    def move_low(source, target, priority_treshold):
        if is_country_ok(source, target):
            _, _, _, release_issues, _ = build.get_release_details(release=source)
            logging.info(f'Выбираем подходящие задачи из релиза {source}')
            for_move = []
            for issue in release_issues:
                if 'сборка' not in issue.fields.summary.lower():
                    if PRIORITY_VALUE[issue.fields.priority.name] <= int(priority_treshold):
                        for_move.append(issue)
            logging.info(f'Найдено {len(for_move)} подходящих задач(-и, -а)')
            logging.info(f'Переносим подходящие задачи в релиз {target}')
            for issue in for_move:
                logging.info(f'Переносим задачу {issue}, {issue.fields.status.name}')
                issue.update(fields={
                    "fixVersions": [{"name": target, }]
                })
            logging.info(f'Перенос выполнен')
        else:
            logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
            raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')

    def move_high(source, target, priority_treshold):
        if is_country_ok(source, target):
            _, _, _, release_issues, _ = build.get_release_details(release=source)
            logging.info(f'Выбираем подходящие задачи из релиза {source}')
            for_move = []
            for issue in release_issues:
                if 'сборка' not in issue.fields.summary.lower():
                    if PRIORITY_VALUE[issue.fields.priority.name] >= int(priority_treshold):
                        for_move.append(issue)
            logging.info(f'Найдено {len(for_move)} подходящих задач(-и, -а)')
            logging.info(f'Переносим подходящие задачи в релиз {target}')
            for issue in for_move:
                logging.info(f'Переносим задачу {issue}, {issue.fields.status.name}')
                issue.update(fields={
                    "fixVersions": [{"name": target, }]
                })
            logging.info(f'Перенос выполнен')
        else:
            logging.exception('Ошибка при вводе релиза-источника и релиза-назначения!')
            raise Exception('Ошибка при вводе релиза-источника и релиза-назначения!')
    #
    # Получаем данные из командной строки
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
                if argv[1] == '-g':
                    source = argv[2]
                    target = argv[3]
                    move_good(source, target)
                elif argv[1] == '-q':
                    source = argv[2]
                    target = argv[3]
                    move_qa(source, target)
                elif argv[1] == '-l':
                    priority_treshold = argv[2]
                    source = argv[3]
                    target = argv[4]
                    move_low(source, target, priority_treshold)
                elif argv[1] == '-h':
                    priority_treshold = argv[2]
                    source = argv[3]
                    target = argv[4]
                    move_high(source, target, priority_treshold)
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

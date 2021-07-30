import os
from random import shuffle

from constants import TESTERS, STATUS_READY, STATUS_FOR_RELEASE
from build import Build

""" Переназначает задачи текущего релиза между тестировщиками """


def main():
    os.makedirs('logs', exist_ok=True)
    build = Build()
    _, release_input, _, fix_issues, _ = build.get_release_details()
    testers = list(TESTERS.keys())
    shuffle(testers)
    delta = 0  # offset for TESTERS in case of issue assign skip
    for index, issue in enumerate(fix_issues):
        if 'сборка' in issue.fields.summary.lower():
            delta += 1
            continue
        if issue.fields.status.name in STATUS_READY or issue.fields.status.name not in STATUS_FOR_RELEASE:
            delta += 1
            continue
        new_assignee = testers[(index - delta) % len(testers)]

        issue.update(fields={
                'assignee': {'name': new_assignee}
            })


if __name__ == '__main__':
    main()

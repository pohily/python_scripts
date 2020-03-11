import shelve
from configparser import ConfigParser
from sys import argv

import gitlab

from merge_requests import PROJECTS_WITH_TESTS, DOCKER_PROJECTS

""" с помощью следующей команды можно запустить тесты в остальных проектах, пропущенные при создании сборки. 
Так как в этом случае запускается только сборка контейнеров докера, тесты автоматически не запускаются.
"""

if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    try:
        release_input = argv[1]
    except IndexError:
        raise Exception('Enter release name')
    RC_name = f'rc-{release_input.replace(".", "-")}'
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])

    with shelve.open('used_projects') as used_projects:
        if RC_name in used_projects:
            for pr in used_projects[RC_name]:
                if pr in PROJECTS_WITH_TESTS and pr not in DOCKER_PROJECTS:
                    project = gl.projects.get(pr)
                    try:
                        branch = project.branches.get(RC_name)
                        try:
                            commit_json = {
                                "branch": f"{RC_name}",
                                "commit_message": "start pipeline commit",
                                "actions": [
                                    {
                                        "action": "update",
                                        "file_path": f"last_build",
                                        "content": f"{RC_name}"
                                    },
                                ]
                            }
                            commit = project.commits.create(commit_json)
                        except gitlab.exceptions.GitlabCreateError:
                            commit_json = {
                                "branch": f"{RC_name}",
                                "commit_message": "start pipeline commit",
                                "actions": [
                                    {
                                        "action": "create",
                                        "file_path": f"last_build",
                                        "content": f"{RC_name}"
                                    },
                                ]
                            }
                            commit = project.commits.create(commit_json)
                    except gitlab.exceptions.GitlabGetError:
                        pass
        else:
            print(f'Сначала надо создать сборку для {RC_name}')


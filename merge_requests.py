import gitlab
from configparser import ConfigParser


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])
    projects = gl.projects.list()
    python_scripts = projects[3]
    branches = python_scripts.branches.list()
    at_85 = branches[0]
    pass


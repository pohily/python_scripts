from configparser import ConfigParser

import gitlab


def main():
    """ Выводит список последних добавленных пользователей гитлаба """
    config = ConfigParser()
    config.read('config.ini')
    gl = gitlab.Gitlab('https://gitlab.4slovo.ru/', private_token=config['user_data']['GITLAB_PRIVATE_TOKEN'])

    users = gl.users.list()  # последние 20
    for number in range(150):
        try:
            user = gl.users.get(number)
            if user.attributes['state'] == 'active':
                print(f"{user.attributes['id']}: "
                      f"{user.attributes['name']} - "
                      f"{user.attributes['username']}")
        except:
            pass


if __name__ == '__main__':
    main()
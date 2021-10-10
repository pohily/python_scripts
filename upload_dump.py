import paramiko
import sys
from build import ConfigParser


def connect_by_ssh():
    country = get_country()
    config = ConfigParser()
    config.read('config.ini')
    server = config['staging'][f'host_{country}']
    username = config['staging'][f'user_{country}']
    password = config['staging'][f'staging_password_{country}']
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port=22, username=username, password=password)


def get_country():
    try:
        if sys.argv[1] == 'ru':
            return 'ru'
        elif sys.argv[1] == 'kz':
            return 'kz'
        elif sys.argv[1] and sys.argv[1] != 'ru' and sys.argv[1] != 'kz':
            raise TypeError("Название страны неверно")
    except IndexError:
        raise IndexError("Не передано название страны")


def main():
    connect_by_ssh()


if __name__ == '__main__':
    main()

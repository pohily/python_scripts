import paramiko
import sys
from build import ConfigParser


class Staging:

    def __init__(self):
        self.country = self.get_country()
        self.client = self.server = self.username = self.password = None
        self.locale = None

    def connect(self):
        config = ConfigParser()
        config.read('config.ini')
        self.server = config['staging'][f'host_{self.country}']
        self.username = config['staging'][f'user_{self.country}']
        self.password = config['staging'][f'staging_password_{self.country}']
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.server, port=22, username=self.username, password=self.password)
        return self.client

    def get_country(self):
        try:
            if sys.argv[1] == 'ru':
                self.country = 'ru'
            elif sys.argv[1] == 'kz':
                self.country = 'kz'
            elif sys.argv[1] and sys.argv[1] != 'ru' and sys.argv[1] != 'kz':
                raise TypeError("Неверно название страны")
        except IndexError:
            raise IndexError("Не передано название страны")
        return self.country

    def upload_frontend_dump(self):
        self.connect()
        cmd_login = 'sudo -Siu n4slovo ' if self.country == 'ru' else 'sudo -Siu kz_f '
        command = cmd_login + f'mysql -u {self.username} -p {self.country}_frontend < {self.country}_frontend.sql'
        _, ssh_stdout, _ = self.client.exec_command(command)
        self.client.close()


def main():
    upload_dump_to_staging = Staging()
    upload_dump_to_staging.connect()


if __name__ == '__main__':
    main()

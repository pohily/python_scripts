import paramiko
import sys
from build import ConfigParser
from tqdm import tqdm


class Staging:

    def __init__(self):
        self.country = self.get_country()
        self.client = self.server = self.username = self.password = None
        self.locale = self.staging_ru_password_backend_database = None

    def connect(self):
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

    def upload_backend_dump(self):
        self.connect()
        if self.country == 'kz':
            cmd_login = 'sudo -Siu kz_{} '
            for postfix in ['crm:', 'backend_mfo:_mfo']:
                postfix_list = postfix.split(':')
                postfix_login = postfix_list[0]
                postfix_db = postfix_list[1]
                command = cmd_login.format(postfix_login) +\
                    f'mysql -u {self.username} -p {self.country}_backend{postfix_db}' \
                    f' < {self.country}_backend{postfix_db}.sql'
                self.client.exec_command(command)
        elif self.country == 'ru':

            cmd_login = 'sudo -Siu crm4slovo '
            command = cmd_login + f'mysql -u {self.country}_backend -p {self.staging_ru_password_backend_database}' \
                                  f' {self.country}_backend < dumps/mariadb/{self.country}_backend.sql'
            _, ssh_stdout, _ = self.client.exec_command(command)
            result = ssh_stdout.read().decode('utf-8').strip("\n")
        self.client.close()

    def get_config_data(self):
        config = ConfigParser()
        config.read('config.ini')
        self.server = config['staging'][f'host_{self.country}']
        self.username = config['staging'][f'user_{self.country}']
        self.password = config['staging'][f'staging_password_{self.country}']
        self.staging_ru_password_backend_database = \
            config['staging'][f'staging_{self.country}_password_backend_database']


def main():
    staging = Staging()
    t = tqdm()
    tqdm.display(t, msg="Прогресс загрузки дампов", pos=None)
    for call in ['get_config_data', 'connect', 'upload_backend_dump']:
        eval(f'staging.{call}()')


if __name__ == '__main__':
    main()

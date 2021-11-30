import sys

import paramiko
from tqdm import tqdm

from build import ConfigParser


class Staging:

    def __init__(self):
        self.country = self.get_country()
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.client = None
        self.server = self.config['staging'][f'host_{self.country}']
        self.username = self.config['staging'][f'user_{self.country}']
        self.password = self.config['staging'][f'staging_password_{self.country}']
        self.staging_frontend_user_database = self.config['staging'][f'staging_{self.country}_frontend_user_database']
        self.staging_backend_user_database = self.config['staging'][f'staging_{self.country}_backend_user_database']
        self.staging_finance_user_database = self.config['staging'][f'staging_{self.country}_finance_user_database']
        self.staging_frontend_password_database = \
            self.config['staging'][f'staging_{self.country}_frontend_password_database']
        self.staging_backend_password_database = \
            self.config['staging'][f'staging_{self.country}_backend_password_database']
        self.staging_finance_password_database = \
            self.config['staging'][f'staging_{self.country}_finance_password_database']
        self.staging_frontend_base_name = self.config['staging'][f'staging_{self.country}_frontend_base_name']
        self.staging_backend_base_name = self.config['staging'][f'staging_{self.country}_backend_base_name']
        self.staging_finance_base_name = self.config['staging'][f'staging_{self.country}_finance_base_name']
        self.frontend_path = 'dumps/docker/frontend_dump.sql'
        self.backend_path = 'dumps/docker/backend_dump.sql'
        self.finance_path = 'dumps/docker/finance_dump.sql'
        self.cmd_login = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.server, port=22, username=self.username, password=self.password)
        return self.client

    def get_country(self):
        try:
            if sys.argv[1] == 'upload_dumps' and sys.argv[2] == 'ru':
                self.country = 'ru'
            elif sys.argv[1] == 'upload_dumps' and sys.argv[2] == 'kz':
                self.country = 'kz'
            elif sys.argv[1] and sys.argv[2] and sys.argv[2] != 'ru' and sys.argv[2] != 'kz':
                raise TypeError("Неверно название страны")
        except IndexError:
            raise IndexError("Не передана команда для загрузки дампов или название страны")
        return self.country

    def upload_frontend_dump(self):
        self.connect()
        self.get_cmd_login()
        command = f'{self.cmd_login} cat {self.frontend_path} | ' + self.cmd_login + ' ' \
                  f'mysql -u{self.staging_frontend_user_database} ' \
                  f'-p{self.staging_frontend_password_database} {self.staging_frontend_base_name}'
        _, ssh_stdout, _ = self.client.exec_command(command)
        result = ssh_stdout.read().decode('utf-8').strip("\n")
        self.client.close()
        return result

    def upload_backend_dump(self):
        self.connect()
        self.get_cmd_login()
        command = f'{self.cmd_login} cat {self.backend_path} | ' + self.cmd_login + ' ' \
                  f'mysql -u{self.staging_backend_user_database} ' \
                  f'-p{self.staging_backend_password_database} {self.staging_backend_base_name}'
        _, ssh_stdout, _ = self.client.exec_command(command)
        result = ssh_stdout.read().decode('utf-8').strip("\n")
        self.client.close()
        return result

    def upload_finance_dump(self):
        self.connect()
        self.get_cmd_login()
        command = f'{self.cmd_login} cat {self.finance_path} | ' + self.cmd_login + ' ' \
                  f'mysql -u{self.staging_finance_user_database} ' \
                  f'-p{self.staging_finance_password_database} {self.staging_finance_base_name}'
        _, ssh_stdout, _ = self.client.exec_command(command)
        result = ssh_stdout.read().decode('utf-8').strip("\n")
        self.client.close()
        return result

    def get_cmd_login(self):
        self.cmd_login = 'sudo -Siu crm4slovo' if self.country == 'ru' else 'sudo -Siu kz_backend_mfo'
        return self.cmd_login

    def run_migration(self):
        self.connect()
        self.get_cmd_login()
        command = f'{self.cmd_login} bash -c "cd ~/httpdocs && vendor/bin/phinx m"'
        _, ssh_stdout, _ = self.client.exec_command(command)
        result = ssh_stdout.read().decode('utf-8').strip("\n")
        self.client.close()
        return result


def main():
    staging = Staging()
    t = tqdm()
    for method in tqdm(['upload_frontend_dump()']):
        tqdm.display(t, msg="Загружаю дамп во фронтенд", pos=None)
        eval(f'staging.{method}')
    for method in tqdm(['upload_backend_dump()']):
        tqdm.display(t, msg="Загружаю дамп в бекенд", pos=None)
        eval(f'staging.{method}')
    for method in tqdm(['upload_finance_dump()']):
        tqdm.display(t, msg="Чищу финансовый модуль", pos=None)
        eval(f'staging.{method}')
    for method in tqdm(['run_migration()']):
        tqdm.display(t, msg="Накатываю миграции", pos=None)
        eval(f'staging.{method}')


if __name__ == '__main__':
    main()

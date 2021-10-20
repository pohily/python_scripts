import paramiko
import sys
from build import ConfigParser
from tqdm import tqdm


class Staging:

    def __init__(self):
        self.country = self.get_country()
        self.client = self.server = self.username = self.password = None
        self.staging_frontend_user_database = self.staging_backend_user_database = None
        self.locale = self.staging_frontend_password_database = self.staging_backend_password_database = None
        self.staging_finance_user_database = self.staging_finance_password_database =\
            self.staging_finance_base_name = None
        self.staging_frontend_base_name = self.staging_backend_base_name = None
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

    def get_config_data(self):
        config = ConfigParser()
        config.read('config.ini')
        self.server = config['staging'][f'host_{self.country}']
        self.username = config['staging'][f'user_{self.country}']
        self.password = config['staging'][f'password_{self.country}']
        self.staging_frontend_user_database = config['staging'][f'staging_{self.country}_frontend_user_database']
        self.staging_backend_user_database = config['staging'][f'staging_{self.country}_backend_user_database']
        self.staging_finance_user_database = config['staging'][f'staging_{self.country}_finance_user_database']
        self.staging_frontend_password_database = \
            config['staging'][f'staging_{self.country}_frontend_password_database']
        self.staging_backend_password_database = \
            config['staging'][f'staging_{self.country}_backend_password_database']
        self.staging_finance_password_database = \
            config['staging'][f'staging_{self.country}_finance_password_database']
        self.staging_frontend_base_name = config['staging'][f'staging_{self.country}_frontend_base_name']
        self.staging_backend_base_name = config['staging'][f'staging_{self.country}_backend_base_name']
        self.staging_finance_base_name = config['staging'][f'staging_{self.country}_finance_base_name']

    def get_cmd_login(self):
        self.cmd_login = 'sudo -Siu crm4slovo' if self.country == 'ru' else 'sudo -Siu kz_backend_mfo'
        return self.cmd_login

    def run_migration(self):
        self.connect()
        self.get_cmd_login()
        commands = [self.cmd_login, 'cd httpdocs', 'vendor/bin/phinx m']
        for command in commands:
            _, ssh_stdout, _ = self.client.exec_command(command)
            result = ssh_stdout.read().decode('utf-8').strip("\n")
        self.client.close()
        return result


def main():
    staging = Staging()
    t = tqdm()
    staging.get_config_data()
    for method in tqdm(['upload_frontend_dump()', 'upload_backend_dump()', 'upload_finance_dump()']):
        tqdm.display(t, msg="Загрузка дампов", pos=None)
        eval(f'staging.{method}')
    for method in tqdm(['run_migration()']):
        tqdm.display(t, msg="Накатывание миграций", pos=None)
        eval(f'staging.{method}')


if __name__ == '__main__':
    main()

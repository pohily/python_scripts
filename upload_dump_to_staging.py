import paramiko
import sys
from build import ConfigParser


class UploadDumpToStaging:

    def __init__(self):
        self.country = self.get_country()

    def connect_to_satging(self):
        config = ConfigParser()
        config.read('config.ini')
        server = config['staging'][f'host_{self.country}']
        username = config['staging'][f'user_{self.country}']
        password = config['staging'][f'staging_password_{self.country}']
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port=22, username=username, password=password)

    def get_country(self):
        try:
            if sys.argv[1] == 'ru':
                return 'ru'
            elif sys.argv[1] == 'kz':
                return 'kz'
            elif sys.argv[1] and sys.argv[1] != 'ru' and sys.argv[1] != 'kz':
                raise TypeError("Неверно название страны")
        except IndexError:
            raise IndexError("Не передано название страны")


def main():
    upload_dump_to_staging = UploadDumpToStaging()
    upload_dump_to_staging.connect_to_satging()


if __name__ == '__main__':
    main()

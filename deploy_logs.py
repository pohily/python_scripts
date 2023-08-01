from datetime import datetime

import paramiko

from constants import PROJECTS_NUMBERS, SYSTEM_USERS, COUNTRIES_ABBR
from build import Build

""" Показывает деплой логи всех измененных в релизе проектов"""


def main():
    build = Build()
    _, release_input, release_country, fix_issues, _ = build.get_release_details()
    release_country = COUNTRIES_ABBR[release_country]
    used_projects = set()
    print(f'\033[34m Выбираем проекты релиза {release_input}\033[0m')
    for issue_number in fix_issues:
        MR_count = build.get_merge_requests(issue_number=issue_number, return_merged=True)
        for merge in MR_count:
            used_projects.add(merge.project)

    projects = [PROJECTS_NUMBERS[pr] for pr in used_projects]
    system_users = [SYSTEM_USERS[release_country][pr] for pr in projects]
    system_users = [user for user in system_users if user]

    username = build.config['staging'][f"user_{release_country}"]
    password = build.config['staging'][f"staging_password_{release_country}"]

    if release_country == 'ru':
        server = 'staging.4slovo.ru'
    else:
        server = 'kz.staging.4slovo.ru'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port=22, username=username, password=password, )

    today = datetime.now().strftime("%Y-%m-%d")
    if 'n4slovo' in system_users:
        system_users += ['ru_lk', 'partner4slovo']
    for user in system_users:
        cmd = f"sudo -Siu {user} awk '/{today}/ ? ++i : i' logs/deploy.log"
        _, ssh_stdout, stderr = client.exec_command(cmd)
        err = stderr.read().decode('utf-8').strip("\n")
        if err:
            print(f'!!!!!!! Error in {user}: {err}')
        else:
            result = ssh_stdout.read().decode('utf-8').strip("\n")
            print(f'{user} ================ Ok. {result}')
            if '[RuntimeException]' in result or 'Fatal:' in result:
                print('\033[31m!!!!!!!!!!!!!!!!Есть ошибки!!!!!!!!!!!!!!!!!\033[0m')
        print(f'\033[34m Деплой лог для {user}\033[0m')
        input('Нажмите Enter для продолжения')
    client.close()


if __name__ == '__main__':
    main()

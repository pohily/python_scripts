PROJECTS_NAMES = {"4slovo.ru/chestnoe_slovo": 7, "4slovo.ru/4slv":10, "4slovo.kz/crm4slovokz": 11,
                  "4slovo.kz/4slovokz": 12, "4slovo.ru/chestnoe_slovo_backend": 20, "4slovo.ru/common": 22,
                  "mrloan.ge/mrloange": 23, "mrloan.ge/crmmrloange": 24, "4slovo.ru/fias": 61,
                  "4slovo.ru/chestnoe_slovo_landing": 62, "4slovo.ru/api": 79, "4slovo/cache": 86, "4slovo/sawmill": 90,
                  "4slovo/common": 91, "4slovo/inn": 92,"4slovo/finance": 93, "docker/finance": 94, "docker/api": 97,
                  "docker/ge": 100, "4slovo/finance_client": 103, "docker/kz": 110, "4slovo/rabbitclient": 113,
                  "4slovo/fs-client": 116, "4slovo/fs": 117, "4slovo/enum-generator": 121, "4slovo/expression": 125,
                  "almal.ge/almalge": 128, "almal.ge/crmalmalge": 129, "4slovo.ru/python-tests": 130,
                  "4slovo/logging": 135, "4slovo/timeservice": 138, "4slovo/timeservice_client": 139,
                  "docker/replicator": 144, "4slovo.ru/python-scripts": 154, "4slovo.kz/landing": 159, "docker/ru": 166,
                  "docker/ru-db": 167, "docker/fias": 172, "4slovo/anonymize-replicator": 178, "module/msm": 187,
                  "4slovo/anon-server": 194, "docker/external_images": 201, "sites/4slokz": 204,
                  "4slovo/sumsub-client": 207
                  }

PROJECTS_NUMBERS = {7: "4slovo.ru/chestnoe_slovo",10: "4slovo.ru/4slv",  11: "4slovo.kz/crm4slovokz",
                    12: "4slovo.kz/4slovokz", 20: "4slovo.ru/chestnoe_slovo_backend", 22: "4slovo.ru/common",
                    23: "mrloan.ge/mrloange", 24: "mrloan.ge/crmmrloange", 61: "4slovo.ru/fias",
                    62: "4slovo.ru/chestnoe_slovo_landing", 79: "4slovo.ru/api", 86: "4slovo/cache",
                    90: "4slovo/sawmill", 91: "4slovo/common", 92: "4slovo/inn", 93: "4slovo/finance",
                    94: "docker/finance", 97: "docker/api", 100: "docker/ge",
                    103: "4slovo/finance_client", 110: "docker/kz", 113: "4slovo/rabbitclient", 116: "4slovo/fs-client",
                    117: "4slovo/fs", 121: "4slovo/enum-generator", 125: "4slovo/expression", 128: "almal.ge/almalge",
                    129: "almal.ge/crmalmalge", 130: "4slovo.ru/python-tests", 135: "4slovo/logging",
                    138: "4slovo/timeservice", 139: "4slovo/timeservice_client", 144: "docker/replicator",
                    154: "4slovo.ru/python-scripts", 159: "4slovo.kz/landing", 166: "docker/ru",167: "docker/ru-db",
                    172: "docker/fias", 178: "4slovo/anonymize-replicator", 187: "module/msm",
                    194: "4slovo/anon-server", 201: "docker/external_images", 204: "sites/4slokz",
                    207: "4slovo/sumsub-client"
                    }

PROJECTS_COUNTRIES = {7: "ru", 10: "ru", 11: "kz", 12: "kz", 20: "ru", 22: "kz", 23: "ge", 24: "ge", 61: "ru",
                      62: "ru", 79: "ru", 86: "ru, kz, ge", 90: "ru, kz, ge", 91: "ru, kz, ge", 92: "ru, kz, ge",
                      93: "ru, kz, ge", 94: "ru, kz, ge", 97: "ru, kz, ge", 100: "ge", 103: "ru, kz, ge", 110: "kz",
                      113: "ru, kz, ge", 116: "ru, kz, ge", 117: "ru, kz, ge", 121: "ge", 125: "ru, kz, ge",
                      128: "ge", 129: "ge", 130: "ru", 135: "ru, kz, ge", 138: "ru, kz, ge", 139: "ru, kz, ge",
                      144: "ru, kz, ge", 154: "ru", 159: "kz", 166: "ru", 167: "ru", 172: "ru, kz", 178: "ru, kz",
                      187: "ru", 194: "ru, kz", 201: "ru, kz, ge", 204: "kz", 207: "ru, kz, ge"
                      }

COUNTRIES = {
    'ru': 'Россия', 'kz': 'Казахстан', 'ge': 'Грузия'
}
COUNTRIES_ABBR = {
    'Россия': 'ru', 'Казахстан': 'kz', 'Грузия':'ge'
}

SYSTEM_USERS = {
    'ru': {
        '4slovo/finance': 'ru_finance', '4slovo/fs': 'fs4slovo', '4slovo.ru/chestnoe_slovo': 'f4slovo',
        '4slovo.ru/chestnoe_slovo_backend': 'crm4slovo', '4slovo.ru/chestnoe_slovo_landing': 'n4slovo',
        '4slovo.ru/api': 'api4slovo', '4slovo.ru/4slv': 'ru_4slv', 'module/msm': '', 'docker/ru': '',
        '4slovo/finance_client': '', '4slovo/anonymize-replicator': '', 'docker/external_images': '',
        'docker/finance': '', '4slovo/anon-server': '', '4slovo/logging': '', '4slovo/expression': '',
        '4slovo.ru/common': '', '4slovo/common': '', '4slovo/sawmill': ''
    },
    'ru2': {
        '4slovo/finance': 'ru_finance', '4slovo/fs': 'ru_fs', '4slovo.ru/chestnoe_slovo': 'ru_frontend',
        '4slovo.ru/chestnoe_slovo_backend': 'ru_backend', '4slovo.ru/chestnoe_slovo_landing': 'ru_frontend_new',
        '4slovo.ru/api': 'ru_api', '4slovo.ru/4slv': 'ru_4slv', 'module/msm': '', 'docker/ru': '',
        '4slovo/finance_client': '', '4slovo/anonymize-replicator': '', 'docker/external_images': '',
        'docker/finance': '', '4slovo/anon-server': '', '4slovo/logging': '', '4slovo/expression': '',
        '4slovo.ru/common': '', '4slovo/common': '', '4slovo/sawmill': ''
    },
    'kz': {
        '4slovo/finance': 'kz_finance', '4slovo/fs': 'kz_fs', '4slovo.kz/4slovokz': 'kz_f',
        '4slovo.kz/crm4slovokz': 'kz_backend_mfo', 'docker/kz': '', '4slovo/sumsub-client': '', 'sites/4slokz': ''
    },
    'kz2': {
        '4slovo/finance': 'kz_finance', '4slovo/fs': 'kz_fileshare', '4slovo.kz/4slovokz': 'kz_frontend',
        '4slovo.kz/crm4slovokz': 'kz_backend_mfo', 'docker/kz': '', '4slovo/sumsub-client': '', 'sites/4slokz': ''
    }
}

MR_STATUS = {
    True: '(x) Конфликт!, ', False: '(/) Нет конфликтов, ',
    'can_be_merged': '(/) Нет конфликтов, ', 'cannot_be_merged': '(x) Конфликт!, ', 'unchecked': '(/) Нет конфликтов,',
    'cannot_be_merged_recheck': '(x) Конфликт!, ','checking': '(x) Конфликт!, ',
}
PRIORITY = {'Critical': '(*r) - Critical', 'Highest': '(!) - Highest', 'High': '(*) - High', 'Medium': '(*g) - Medium',
            'Low': '(*b) - Low', 'Lowest': '(*b) - Lowest', 'Критический': '(*r) - Critical',
            'MEGA Critical': '(flag) - MEGA Critical'}
STATUS_FOR_RELEASE = ['MEGA Critical', 'Released to production', 'Passed QA', 'In regression test', 'Ready for release',
    'Закрыт', 'Fixed', 'Closed', 'Готово'
    ]#, 'Ready for review', 'Ready for technical solution review', 'In QA','Open', 'Ready for QA', 'In development']
STATUS_READY = ['Released to production', 'Ready for release', 'Закрыт', 'Fixed', 'Closed']

TESTERS = {
    'i.chechikov': 76,
    'm.pohilyj': 77,
    'g.kozlov': 99,
    'a.melnik': 101
}

PROJECTS_WITH_TESTS = [11, 20, 61, 79, 93, 94, 97, 100, 110, 166, 172, 178, 187, 194, 201]
PROJECTS_WITHOUT_STAGING = [22, 61, 86, 90, 91, 92, 103, 113, 116, 121, 125, 135, 138, 139, 172, 178, 194, 204, 207]
DOCKER_PROJECTS = [94, 97, 100, 110, 166, 167, 172, 187, 201]

GIT_LAB = 'https://gitlab'
ISSUE_URL = 'https://jira.4slovo.ru/browse/'
JIRA_SERVER = 'https://jira.4slovo.ru/'
MR_BY_IID = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?iids[]={}&{}&"with_merge_status_recheck"=True'
RELEASE_ISSUES_URL = 'https://jira.4slovo.ru/rest/api/latest/search?jql=fixVersion={}'
RELEASE_URL = 'https://jira.4slovo.ru/projects/SLOV/versions/{}'
REMOTE_LINK = 'https://jira.4slovo.ru/rest/api/latest/issue/{}/remotelink'

SMTP_PORT = 587
SMTP_SERVER = 'smtp.4slovo.ru'

TEST = False

if __name__ == '__main__':
    import re
    with open('/Users/user/Desktop/1.txt', 'r') as text:
        for line in text:
            pids = re.findall(r'2785\d+', line)
    with open('/Users/user/Desktop/2.csv', 'w') as file:
        for pid in sorted(set(pids)):
            line = str(pid) + '\n'
            file.write(line)
PROJECTS_NAMES = {"4slovo.ru/chestnoe_slovo": 7, "4slovo.kz/crm4slovokz": 11, "4slovo.kz/4slovokz": 12,
                  "4slovo.ru/chestnoe_slovo_backend": 20, "4slovo.ru/common": 22, "mrloan.ge/mrloange": 23,
                  "mrloan.ge/crmmrloange": 24, "4slovo.ru/fias": 61, "4slovo.ru/chestnoe_slovo_landing": 62,
                  "4slovo.ru/api": 79, "4slovo/cache": 86, "4slovo/sawmill": 90, "4slovo/common": 91, "4slovo/inn": 92,
                  "4slovo/finance": 93, "docker/finance": 94, "docker/api": 97, "docker/ge": 100,
                  "4slovo/finance_client": 103, "docker/kz": 110, "4slovo/rabbitclient": 113, "4slovo/fs-client": 116,
                  "4slovo/fs": 117, "4slovo/enum-generator": 121, "4slovo/expression": 125, "almal.ge/almalge": 128,
                  "almal.ge/crmalmalge": 129, "4slovo.ru/python-tests": 130, "4slovo/logging": 135,
                  "4slovo/timeservice": 138, "4slovo/timeservice_client": 139, "docker/replicator": 144,
                  "4slovo.ru/python-scripts": 154, "4slovo.kz/landing": 159, "docker/ru": 166, "docker/ru-db": 167,
                  }

PROJECTS_NUMBERS = {7: "4slovo.ru/chestnoe_slovo", 11: "4slovo.kz/crm4slovokz", 12: "4slovo.kz/4slovokz",
                    20: "4slovo.ru/chestnoe_slovo_backend", 22: "4slovo.ru/common", 23: "mrloan.ge/mrloange",
                    24: "mrloan.ge/crmmrloange", 61: "4slovo.ru/fias", 62: "4slovo.ru/chestnoe_slovo_landing",
                    79: "4slovo.ru/api", 86: "4slovo/cache", 90: "4slovo/sawmill", 91: "4slovo/common",
                    92: "4slovo/inn", 93: "4slovo/finance", 94: "docker/finance", 97: "docker/api", 100: "docker/ge",
                    103: "4slovo/finance_client", 110: "docker/kz", 113: "4slovo/rabbitclient", 116: "4slovo/fs-client",
                    117: "4slovo/fs", 121: "4slovo/enum-generator", 125: "4slovo/expression", 128: "almal.ge/almalge",
                    129: "almal.ge/crmalmalge", 130: "4slovo.ru/python-tests", 135: "4slovo/logging",
                    138: "4slovo/timeservice", 139: "4slovo/timeservice_client", 144: "docker/replicator",
                    154: "4slovo.ru/python-scripts", 159: "4slovo.kz/landing", 166: "docker/ru",167: "docker/ru-db",
                    }

PROJECTS_COUNTRIES = {7: "ru", 11: "kz", 12: "kz", 20: "ru", 22: "ru", 23: "ge", 24: "ge", 61: "ru",
                      62: "ru", 79: "ru", 86: "ru, kz, ge", 90: "ru, kz, ge", 91: "ru, kz, ge", 92: "ru, kz, ge",
                      93: "ru, kz, ge", 94: "ru, kz, ge", 97: "ru, kz, ge", 100: "ge", 103: "ru, kz, ge", 110: "kz",
                      113: "ru, kz, ge", 116: "ru, kz, ge", 117: "ru, kz, ge", 121: "ge", 125: "ru, kz, ge",
                      128: "ge", 129: "ge", 130: "ru", 135: "ru, kz, ge", 138: "ru, kz, ge", 139: "ru, kz, ge",
                      144: "ru, kz, ge", 154: "ru", 159: "kz", 166: "ru", 167: "ru",
                      }

MR_STATUS = {'can_be_merged': '(/) Нет конфликтов, ', 'cannot_be_merged': '(x) Конфликт!, '}
PRIORITY = {'Critical': '(!) - Critical', 'Highest': '(*r) - Highest', 'High': '(*) - High', 'Medium': '(*g) - Medium',
            'Low': '(*b) - Low', 'Lowest': '(*b) - Lowest', 'Критический': '(!) - Critical'}

PROJECTS_WITH_TESTS = [11, 20, 79, 93, 94, 97, 100, 110, 166]
DOCKER_PROJECTS = [94, 97, 100, 110, 166, 167]

ISSUE_URL = 'https://jira.4slovo.ru/browse/'
GIT_LAB = 'https://gitlab'
JIRA_SERVER = 'https://jira.4slovo.ru/'
RELEASE_ISSUES_URL = 'https://jira.4slovo.ru/rest/api/latest/search?jql=fixVersion={}'
RELEASE_URL = 'https://jira.4slovo.ru/projects/SLOV/versions/{}'
REMOTE_LINK = 'https://jira.4slovo.ru/rest/api/latest/issue/{}/remotelink'
STATUS_FOR_RELEASE = ['Released to production', 'Passed QA', 'In regression test', 'Ready for release', 'Закрыт',
                      'Fixed', 'Closed']#, 'In development']
SMTP_PORT = 587
SMTP_SERVER = 'smtp.4slovo.ru'
MR_BY_IID = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?iids[]={}&{}'

TEST = False

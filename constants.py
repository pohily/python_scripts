TEST = False
# Делать ли last_build если уже есть незарелиженная сборка. Чтобы не было конфликтов - можно не делать
MAKE_LAST_BUILD_FILE_AND_START_TESTS = True

PROJECTS_NAMES = {"4slovo.ru/chestnoe_slovo": 7, "4slovo.ru/4slv": 10, "4slovo.kz/crm4slovokz": 11,
                  "4slovo.kz/4slovokz": 12, "4slovo.ru/chestnoe_slovo_backend": 20, "4slovo.ru/common": 22,
                  "mrloan.ge/mrloange": 23, "mrloan.ge/crmmrloange": 24, "4slovo.ru/fias": 61,
                  "4slovo.ru/chestnoe_slovo_landing": 62, "4slovo.ru/api": 79, "4slovo/cache": 86, "4slovo/sawmill": 90,
                  "4slovo/common": 91, "4slovo/inn": 92, "4slovo/finance": 93, "docker/finance": 94, "docker/api": 97,
                  "docker/ge": 100, "4slovo/finance_client": 103, "docker/finance_client": 104,
                  "docker/kz": 110, "4slovo/rabbitclient": 113, "4slovo/fs-client": 116,
                  "4slovo/fs": 117, "4slovo/enum-generator": 121, "4slovo/expression": 125,
                  "almal.ge/almalge": 128, "almal.ge/crmalmalge": 129, "4slovo.ru/python-tests": 130,
                  "4slovo/logging": 135, "4slovo/timeservice": 138, "4slovo/timeservice_client": 139,
                  "docker/replicator": 144, "4slovo.ru/python-scripts": 154, "4slovo.kz/landing": 159, "docker/ru": 166,
                  "docker/ru-db": 167, "docker/kz-db": 171, "docker/fias": 172, "4slovo/anonymize-replicator": 178,
                  "module/message-sender-package": 186,
                  "module/msm": 187, "4slovo/anon-server": 194, "docker/external_images": 201, "sites/4slokz": 204,
                  "4slovo/sumsub-client": 207, "docker/alpine-pkgs-repo": 212, "4slovo/S3Client": 215,
                  "4slovo.ru/osticket": 223, "4slovo/short_link_client": 225, '4slovo/mock-server': 227,
                  "4slovo/event-manager": 228, "4slovo/reflection": 229, "4slovo/cast-type": 230, "4slovo/dto": 231,
                  "4slovo/csv": 232, "4slovo/xxtea": 233, "external/PHPExcel": 240, "4slovo/config": 242,
                  "7payda.kz/7paydakz": 244, "7payda.kz/crm7paydakz": 245, "docker/7paydakz": 246,
                  "docker/7paydakz-db": 247
                  }

PROJECTS_NUMBERS = {7: "4slovo.ru/chestnoe_slovo", 10: "4slovo.ru/4slv", 11: "4slovo.kz/crm4slovokz",
                    12: "4slovo.kz/4slovokz", 20: "4slovo.ru/chestnoe_slovo_backend", 22: "4slovo.ru/common",
                    23: "mrloan.ge/mrloange", 24: "mrloan.ge/crmmrloange", 61: "4slovo.ru/fias",
                    62: "4slovo.ru/chestnoe_slovo_landing", 79: "4slovo.ru/api", 86: "4slovo/cache",
                    90: "4slovo/sawmill", 91: "4slovo/common", 92: "4slovo/inn", 93: "4slovo/finance",
                    94: "docker/finance", 97: "docker/api", 100: "docker/ge", 103: "4slovo/finance_client",
                    104: "docker/finance_client", 110: "docker/kz", 113: "4slovo/rabbitclient", 116: "4slovo/fs-client",
                    117: "4slovo/fs", 121: "4slovo/enum-generator", 125: "4slovo/expression", 128: "almal.ge/almalge",
                    129: "almal.ge/crmalmalge", 130: "4slovo.ru/python-tests", 135: "4slovo/logging",
                    138: "4slovo/timeservice", 139: "4slovo/timeservice_client", 144: "docker/replicator",
                    154: "4slovo.ru/python-scripts", 159: "4slovo.kz/landing", 166: "docker/ru", 167: "docker/ru-db",
                    171: "docker/kz-db", 172: "docker/fias", 178: "4slovo/anonymize-replicator",
                    186: "module/message-sender-package", 187: "module/msm",
                    194: "4slovo/anon-server", 201: "docker/external_images", 204: "sites/4slokz",
                    207: "4slovo/sumsub-client", 212: "docker/alpine-pkgs-repo", 215: "4slovo/S3Client",
                    223: "4slovo.ru/osticket", 225: "4slovo/short_link_client", 227: '4slovo/mock-server',
                    228: "4slovo/event-manager", 229: "4slovo/reflection", 230: "4slovo/cast-type", 231: "4slovo/dto",
                    232: "4slovo/csv", 233: "4slovo/xxtea", 240: "external/PHPExcel", 242: "4slovo/config",
                    244: "7payda.kz/7paydakz", 245: "7payda.kz/crm7paydakz", 246: "docker/7paydakz",
                    247: "docker/7paydakz-db"
                    }

PROJECTS_COUNTRIES = {7: "ru", 10: "ru, kz", 11: "kz", 12: "kz", 20: "ru", 22: "ru, kz, ge, 7da.kz", 23: "ge", 24: "ge",
                      61: "ru", 62: "ru", 79: "ru", 86: "ru, kz, ge, 7da.kz", 90: "ru, kz, ge", 91: "ru, kz, ge",
                      92: "ru, kz, ge", 93: "ru, kz, ge", 94: "ru, kz, ge", 97: "ru, kz, ge", 100: "ge",
                      103: "ru, kz, ge", 104: "ru, kz, ge", 110: "kz", 113: "ru, kz, ge", 116: "ru, kz, ge",
                      117: "ru, kz, ge", 121: "ge", 125: "ru, kz, ge", 128: "ge", 129: "ge", 130: "ru",
                      135: "ru, kz, ge", 138: "ru, kz, ge", 139: "ru, kz, ge", 144: "ru, kz, ge", 154: "ru", 159: "kz",
                      166: "ru", 167: "ru", 171: "kz", 172: "ru, kz", 178: "ru, kz",
                      186: "ru", 187: "ru", 194: "ru, kz",
                      201: "ru, kz, ge", 204: "kz", 207: "ru, kz, ge", 212: "ru, kz, ge", 215: "ru, kz, ge", 223: "ru",
                      225: "ru, kz, ge", 227: "ru, kz, ge", 228: "ru, kz, ge", 229: "", 230: "ru, kz, ge",
                      231: "ru, kz, ge", 232: "ru, kz, ge", 233: "ru, kz, ge", 240: "ru, kz, ge",
                      242: "ru, kz, ge, 7da.kz", 244: "7da.kz", 245: "7da.kz", 246: "7da.kz", 247: "7da.kz"
                      }

COUNTRIES = {
    'ru': 'Россия', 'kz': 'Казахстан', 'ge': 'Грузия', '7da': 'Казахстан'
}
COUNTRIES_ABBR = {
    'Россия': 'ru', 'Казахстан': 'kz', 'Грузия': 'ge'
}

SYSTEM_USERS = {
    'ru': {
        '4slovo/finance': 'ru_finance', '4slovo/fs': 'fs4slovo', '4slovo.ru/chestnoe_slovo': 'f4slovo',
        '4slovo.ru/chestnoe_slovo_backend': 'crm4slovo', '4slovo.ru/chestnoe_slovo_landing': 'n4slovo',
        '4slovo.ru/api': 'api4slovo', '4slovo.ru/4slv': 'ru_4slv', 'module/msm': '', 'docker/ru': '',
        '4slovo/finance_client': '', '4slovo/anonymize-replicator': '', 'docker/external_images': '',
        'docker/finance': '', 'docker/finance_client': '', '4slovo/anon-server': '', '4slovo/logging': '',
        '4slovo/expression': '', '4slovo.ru/common': '', '4slovo/common': '', '4slovo/sawmill': '', 'docker/ru-db': '',
        'docker/fias': '', '4slovo.ru/fias': '', 'docker/alpine-pkgs-repo': '', '4slovo.ru/osticket': '',
        "4slovo/short_link_client": '', '4slovo/mock-server': '', "4slovo/event-manager": '', "4slovo/cast-type": '',
        "4slovo/dto": '', '4slovo/reflection': '', '4slovo/csv': '', '4slovo/xxtea': '',
        '4slovo/cache': '', "4slovo/fs-client": '', "external/PHPExcel": '', 'module/message-sender-package': ''
    },
    'ru2': {
        '4slovo/finance': 'ru_finance', '4slovo/fs': 'ru_fs', '4slovo.ru/chestnoe_slovo': 'ru_frontend',
        '4slovo.ru/chestnoe_slovo_backend': 'ru_backend', '4slovo.ru/chestnoe_slovo_landing': 'ru_frontend_new',
        '4slovo.ru/api': 'ru_api', '4slovo.ru/4slv': 'ru_4slv', 'module/msm': '', 'docker/ru': '',
        '4slovo/finance_client': '', '4slovo/anonymize-replicator': '', 'docker/external_images': '',
        'docker/finance': '', 'docker/finance_client': '', '4slovo/anon-server': '', '4slovo/logging': '',
        '4slovo/expression': '', '4slovo.ru/common': '', '4slovo/common': '', '4slovo/sawmill': '', 'docker/ru-db': '',
        'docker/fias': '', '4slovo.ru/fias': '', 'docker/alpine-pkgs-repo': '', '4slovo.ru/osticket': '',
        "4slovo/short_link_client": '', '4slovo/mock-server': '', "4slovo/event-manager": '', "4slovo/cast-type": '',
        "4slovo/dto": '', '4slovo/reflection': '', '4slovo/csv': '', '4slovo/xxtea': '',
        '4slovo/cache': '', "4slovo/fs-client": '', "external/PHPExcel": '', 'module/message-sender-package': ''
    },
    'kz': {
        '4slovo/finance': 'kz_finance', '4slovo/fs': 'kz_fs', '4slovo.kz/4slovokz': 'kz_f',
        '4slovo.kz/crm4slovokz': 'kz_backend_mfo', 'docker/kz': '', '4slovo/sumsub-client': '', 'sites/4slokz': '',
        'docker/kz-db': '', '4slovo.ru/4slv': '', 'docker/finance': '', 'docker/finance_client': '',
        '4slovo/mock-server': '', '4slovo/sawmill': '', '4slovo/S3Client': '', "4slovo/event-manager": '',
        "4slovo/cast-type": '', "4slovo/dto": '', '4slovo/reflection': '', '4slovo/csv': '', '4slovo/xxtea': '',
        '4slovo/cache': '', "4slovo/fs-client": '', "external/PHPExcel": '', "4slovo/config": '',
        '4slovo.ru/common': '', '7payda.kz/crm7paydakz': 'crm_paydak', '7payda.kz/7paydakz': 'f_paydakz'
    },
    'kz2': {
        '4slovo/finance': 'kz_finance', '4slovo/fs': 'kz_fileshare', '4slovo.kz/4slovokz': 'kz_frontend',
        '4slovo.kz/crm4slovokz': 'kz_backend_mfo', 'docker/kz': '', '4slovo/sumsub-client': '', 'sites/4slokz': '',
        'docker/kz-db': '', '4slovo.ru/4slv': '', 'docker/finance': '', 'docker/finance_client': '',
        '4slovo/mock-server': '', '4slovo/sawmill': '', '4slovo/S3Client': '', "4slovo/event-manager": '',
        "4slovo/cast-type": '', "4slovo/dto": '', '4slovo/reflection': '', '4slovo/csv': '', '4slovo/xxtea': '',
        '4slovo/cache': '', "4slovo/fs-client": '', "external/PHPExcel": '', "4slovo/config": '', '4slovo.ru/common': ''
    }
}

MR_STATUS = {
    True: '(x) Конфликт!, ', False: '(/) Нет конфликтов, ',
    'can_be_merged': '(/) Нет конфликтов, ', 'cannot_be_merged': '(x) Конфликт!, ', 'unchecked': '(/) Нет конфликтов,',
    'cannot_be_merged_recheck': '(x) Конфликт!, ', 'checking': '(x) Конфликт!, ',
}
PRIORITY = {'Critical': '(*r) - Critical', 'Highest': '(!) - Highest', 'High': '(*) - High', 'Medium': '(*g) - Medium',
            'Low': '(*b) - Low', 'Lowest': '(*b) - Lowest', 'Критический': '(*r) - Critical',
            'MEGA Critical': '(flag) - MEGA Critical'}
PRIORITY_VALUE = {
    'MEGA Critical': 1, 'Critical': 2, 'Критический': 2, 'Highest': 3, 'High': 4, 'Medium': 5, 'Low': 6, 'Lowest': 7
}

STATUS_FOR_RELEASE = ['Released to production', 'Passed QA', 'In regression test', 'Ready for release',
                      'Закрыт', 'Fixed', 'Closed', 'Готово'
                      ]  # , 'Ready for review', 'Ready for technical solution review', 'In QA', 'Open', 'Ready for QA', 'In development', 'Reopened', 'Reviewing', 'Technical solution', 'В работе']
STATUS_READY = ['Released to production', 'Ready for release', 'Закрыт', 'Fixed', 'Closed']

STATUS_FOR_QA = ['Ready for QA', 'In QA']

TESTERS = {
    'm.pohilyj': 77,
    'g.kozlov': 99,
    'a.melnik': 101,
    'v.dolinin': 139,
    'a.kuznetsov': 140
}

PROJECTS_WITH_TESTS = [11, 20, 61, 79, 93, 94, 97, 100, 110, 166, 172, 178, 187, 194, 201, 227, 245, 246, 247]
"""
        11: 4slovo.kz/crm4slovokz
        20: 4slovo.ru/chestnoe_slovo_backend
        61: 4slovo.ru/fias
        79: 4slovo.ru/api
        93: 4slovo/finance
        94: docker/finance
        97: docker/api
        100: docker/ge
        110: docker/kz
        166: docker/ru
        172: docker/fias
        178: 4slovo/anonymize-replicator
        187: module/msm
        194: 4slovo/anon-server
        201: docker/external_images
        212: docker/alpine-pkgs-repo
        227: 4slovo/mock-server
        245: 7payda.kz/7paydakz
        246: docker/7paydakz
        247: docker/7paydakz-db
"""
PROJECTS_WITHOUT_STAGING = [
    22, 86, 90, 91, 92, 103, 104, 113, 116, 121, 125, 128, 129, 135, 138, 139, 171, 178, 186, 194, 204, 207, 212, 215,
    225, 227, 228, 229, 230, 231, 232, 233, 240, 242, 246, 247
]
"""
        90: 4slovo/sawmill
        91: 4slovo/common
        92: 4slovo/inn
        103: 4slovo/finance_client
        104: docker/finance_client
        113: 4slovo/rabbitclient
        116: 4slovo/fs-client
        121: 4slovo/enum-generator
        125: 4slovo/expression
        128: almal.ge/almalge
        129: almal.ge/crmalmalge
        135: 4slovo/logging
        138: 4slovo/timeservice
        139: 4slovo/timeservice_client
        171: docker/kz-db
        178: 4slovo/anonymize-replicator
        186: module/message-sender-package
        194: 4slovo/anon-server
        204: sites/4slokz
        207: 4slovo/sumsub-client
        212: docker/alpine-pkgs-repo
        215: 4slovo/S3Client
        225: 4slovo/short_link_client
        227: 4slovo/mock-server
        228: 4slovo/event-manager, 
        229: 4slovo/reflection, 
        230: 4slovo/cast-type, 
        231: 4slovo/dto
        232: 4slovo/csv
        233: 4slovo/xxtea
        240: external/PHPExcel
        242: 4slovo/config
        246: docker/7paydakz
        247: docker/7paydakz-db
"""
DOCKER_PROJECTS = [94, 97, 100, 110, 166, 167, 172, 201, 246, 247]
"""
        94: docker/finance
        97: docker/api
        100: docker/ge
        110: docker/kz
        166: docker/ru
        167: docker/ru-db
        172: docker/fias
        187: module/msm - пока убрали - надо вливать в стейджинг
        201: docker/external_images
        212: docker/alpine-pkgs-repo
        246: docker/7paydakz
        247: docker/7paydakz-db
"""

GIT_LAB = 'https://gitlab'
GIT_LAB_SERVER = 'https://gitlab.4slovo.ru/'
ISSUE_URL = 'https://jira.4slovo.ru/browse/'
JIRA_SERVER = 'https://jira.4slovo.ru/'
JIRA_OPTIONS = {'server': JIRA_SERVER}
CONFLUENCE_SERVER = "https://confluence.4slovo.ru/"
CONFLUENCE_LINK = "https://confluence.4slovo.ru/pages/viewpage.action?pageId={}"
MR_BY_IID = 'https://gitlab.4slovo.ru/api/v4/projects/{}/merge_requests?iids[]={}&{}&"with_merge_status_recheck"=True'
RELEASE_ISSUES_URL = 'https://jira.4slovo.ru/rest/api/latest/search?jql=fixVersion={}'
RELEASE_URL = 'https://jira.4slovo.ru/projects/SLOV/versions/{}'
REMOTE_LINK = 'https://jira.4slovo.ru/rest/api/latest/issue/{}/remotelink'

SMTP_PORT = 587
SMTP_SERVER = 'smtp.4slovo.ru'

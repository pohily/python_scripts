TEST = False
# Делать ли last_build если уже есть незарелиженная сборка. Чтобы не было конфликтов - можно не делать
MAKE_LAST_BUILD_FILE_AND_START_TESTS = True

PROJECTS_NAMES = {"4slovo.ru/chestnoe_slovo": 7,
                  "4slovo.ru/4slv": 10,
                  "4slovo.kz/crm4slovokz": 11,
                  "4slovo.kz/4slovokz": 12,
                  "4slovo.ru/chestnoe_slovo_backend": 20,
                  "4slovo.ru/common": 22,
                  "mrloan.ge/mrloange": 23,
                  "mrloan.ge/crmmrloange": 24,
                  "4slovo.ru/fias": 61,
                  "4slovo.ru/chestnoe_slovo_landing": 62,
                  "4slovo.ru/api": 79,
                  "4slovo/cache": 86,
                  "4slovo/sawmill": 90,
                  "4slovo/common": 91,
                  "4slovo/inn": 92,
                  "4slovo/finance": 93,
                  "docker/finance": 94,
                  "docker/api": 97,
                  "docker/ge": 100,
                  "4slovo/finance_client": 103,
                  "docker/finance_client": 104,
                  "docker/kz": 110,
                  "4slovo/rabbitclient": 113,
                  "4slovo/fs-client": 116,
                  "4slovo/fs": 117,
                  "4slovo/yaml-config": 119,
                  "4slovo/money": 120,
                  "4slovo/enum-generator": 121,
                  "4slovo/registry-generator": 123,
                  "4slovo/interface-generator": 124,
                  "4slovo/expression": 125,
                  "almal.ge/almalge": 128,
                  "almal.ge/crmalmalge": 129,
                  "4slovo.ru/python-tests": 130,
                  "4slovo/logging": 135,
                  "4slovo/timeservice": 138,
                  "4slovo/timeservice_client": 139,
                  "docker/replicator": 144,
                  "4slovo.ru/python-scripts": 154,
                  "4slovo.kz/landing": 159,
                  "docker/ru": 166,
                  "docker/ru-db": 167,
                  "docker/kz-db": 171,
                  "docker/fias": 172,
                  "4slovo/anonymize-replicator": 178,
                  "module/message-sender-package": 186,
                  "module/msm": 187,
                  "4slovo/anon-server": 194,
                  "docker/external_images": 201,
                  "module/rabbitmq": 202,
                  "sites/4slokz": 204,
                  "4slovo/sumsub-client": 207,
                  "docker/alpine-pkgs-repo": 212,
                  "4slovo/S3Client": 215,
                  "4slovo.ru/osticket": 223,
                  "4slovo/short_link_client": 225,
                  '4slovo/mock-server': 227,
                  "4slovo/event-manager": 228,
                  "4slovo/reflection": 229,
                  "4slovo/cast-type": 230,
                  "4slovo/dto": 231,
                  "4slovo/csv": 232,
                  "4slovo/xxtea": 233,
                  "4slovo/satis": 237,
                  "external/PHPExcel": 240,
                  "4slovo/config": 242,
                  "7payda.kz/7paydakz": 244,
                  "7payda.kz/crm7paydakz": 245,
                  "docker/7paydakz": 246,
                  "docker/7paydakz-db": 247,
                  "module/message-scheduler-module": 248,
                  "4slovo/production-profiler": 251,
                  "cards/card-info-recognizer": 252,
                  "docker/ru-db-v2": 253,
                  "4slovo/php-cs-fixer": 254,
                  "4slovo/metrics-provider": 257,
                  "4slovo/satisfy": 259,
                  "4slovo.kz/leasing/front": 262,
                  "4slovo.kz/leasing/crm": 263,
                  "docker/leasing": 264,
                  "docker/leasing-db": 265,
                  "4slovo/db2confluence": 266,
                  "4slovo/test-coverage-checker": 267,
                  "4slovo/osticket": 271,
                  "lemoney.kz/lemoneykz": 272,
                  "lemoney.kz/crmlemoneykz": 273,
                  "docker/lemoneykz": 274,
                  "docker/lemoney-db": 275,
                  "4slovo/4slv": 276,
                  "4slovo.ru/auto-rotate-document": 279,
                  "4slovo/php-heic-to-jpg": 283,
                  }

PROJECTS_NUMBERS = {7: "4slovo.ru/chestnoe_slovo",
                    10: "4slovo.ru/4slv",
                    11: "4slovo.kz/crm4slovokz",
                    12: "4slovo.kz/4slovokz",
                    20: "4slovo.ru/chestnoe_slovo_backend",
                    22: "4slovo.ru/common",
                    23: "mrloan.ge/mrloange",
                    24: "mrloan.ge/crmmrloange",
                    61: "4slovo.ru/fias",
                    62: "4slovo.ru/chestnoe_slovo_landing",
                    79: "4slovo.ru/api",
                    86: "4slovo/cache",
                    90: "4slovo/sawmill",
                    91: "4slovo/common",
                    92: "4slovo/inn",
                    93: "4slovo/finance",
                    94: "docker/finance",
                    97: "docker/api",
                    100: "docker/ge",
                    103: "4slovo/finance_client",
                    104: "docker/finance_client",
                    110: "docker/kz",
                    113: "4slovo/rabbitclient",
                    116: "4slovo/fs-client",
                    117: "4slovo/fs",
                    119: "4slovo/yaml-config",
                    120: "4slovo/money",
                    121: "4slovo/enum-generator",
                    123: "4slovo/registry-generator",
                    124: "4slovo/interface-generator",
                    125: "4slovo/expression",
                    128: "almal.ge/almalge",
                    129: "almal.ge/crmalmalge",
                    130: "4slovo.ru/python-tests",
                    135: "4slovo/logging",
                    138: "4slovo/timeservice",
                    139: "4slovo/timeservice_client",
                    144: "docker/replicator",
                    154: "4slovo.ru/python-scripts",
                    159: "4slovo.kz/landing",
                    166: "docker/ru",
                    167: "docker/ru-db",
                    171: "docker/kz-db",
                    172: "docker/fias",
                    178: "4slovo/anonymize-replicator",
                    186: "module/message-sender-package",
                    187: "module/msm",
                    194: "4slovo/anon-server",
                    201: "docker/external_images",
                    202: "module/rabbitmq",
                    204: "sites/4slokz",
                    207: "4slovo/sumsub-client",
                    212: "docker/alpine-pkgs-repo",
                    215: "4slovo/S3Client",
                    223: "4slovo.ru/osticket",
                    225: "4slovo/short_link_client",
                    227: '4slovo/mock-server',
                    228: "4slovo/event-manager",
                    229: "4slovo/reflection",
                    230: "4slovo/cast-type",
                    231: "4slovo/dto",
                    232: "4slovo/csv",
                    233: "4slovo/xxtea",
                    237: "4slovo/satis",
                    240: "external/PHPExcel",
                    242: "4slovo/config",
                    244: "7payda.kz/7paydakz",
                    245: "7payda.kz/crm7paydakz",
                    246: "docker/7paydakz",
                    247: "docker/7paydakz-db",
                    248: "module/message-scheduler-module",
                    251: "4slovo/production-profiler",
                    252: "cards/card-info-recognizer",
                    253: "docker/ru-db-v2",
                    254: "4slovo/php-cs-fixer",
                    257: "4slovo/metrics-provider",
                    259: "4slovo/satisfy",
                    262: "4slovo.kz/leasing/front",
                    263: "4slovo.kz/leasing/crm",
                    264: "docker/leasing",
                    265: "docker/leasing-db",
                    266: "4slovo/db2confluence",
                    267: "4slovo/test-coverage-checker",
                    271: "4slovo/osticket",
                    272: "lemoney.kz/lemoneykz",
                    273: "lemoney.kz/crmlemoneykz",
                    274: "docker/lemoneykz",
                    275: "docker/lemoney-db",
                    276: "4slovo/4slv",
                    279: "4slovo.ru/auto-rotate-document",
                    283: "4slovo/php-heic-to-jpg",
                    }

PROJECTS_COUNTRIES = {7: "ru",
                      10: "ru, kz",
                      11: "kz",
                      12: "kz",
                      20: "ru",
                      22: "ru, kz, ge, 7da.kz, lemoney.kz",
                      23: "ge",
                      24: "ge",
                      61: "ru",
                      62: "ru",
                      79: "ru",
                      86: "ru, kz, ge, 7da.kz",
                      90: "ru, kz, ge, 7da.kz",
                      91: "ru, kz, ge",
                      92: "ru, kz, ge",
                      93: "ru, kz, ge",
                      94: "ru, kz, ge",
                      97: "ru, kz, ge",
                      100: "ge",
                      103: "ru, kz, ge",
                      104: "ru, kz, ge",
                      110: "kz",
                      113: "ru, kz, ge",
                      116: "ru, kz, ge",
                      117: "ru, kz, ge",
                      119: "ru, kz, ge",
                      120: "ru, kz, ge",
                      121: "ru, kz, ge",
                      123: "ru, kz, ge",
                      124: "ru, kz, ge",
                      125: "ru, kz, ge",
                      128: "ge",
                      129: "ge",
                      130: "ru",
                      135: "ru, kz, ge",
                      138: "ru, kz, ge",
                      139: "ru, kz, ge",
                      144: "ru, kz, ge",
                      154: "ru",
                      159: "kz",
                      166: "ru",
                      167: "ru",
                      171: "kz",
                      172: "ru, kz",
                      178: "ru, kz",
                      186: "ru",
                      187: "ru",
                      194: "ru, kz",
                      201: "ru, kz, ge",
                      202: "ru, kz, ge",
                      204: "kz",
                      207: "ru, kz, ge",
                      212: "ru, kz, ge",
                      215: "ru, kz, ge",
                      223: "ru, kz, ge",
                      225: "ru, kz, ge",
                      227: "ru, kz, ge",
                      228: "ru, kz, ge",
                      229: "ru, kz, ge, 7da.kz, lemoney.kz",
                      230: "ru, kz, ge, 7da.kz, lemoney.kz",
                      231: "ru, kz, ge, 7da.kz, lemoney.kz",
                      232: "ru, kz, ge, 7da.kz, lemoney.kz",
                      233: "ru, kz, ge",
                      237: "ru, kz, ge, 7da.kz, lemoney.kz",
                      240: "ru, kz, ge",
                      242: "ru, kz, ge, 7da.kz, lemoney.kz",
                      244: "7da.kz",
                      245: "7da.kz",
                      246: "7da.kz",
                      247: "7da.kz",
                      248 : "ru",
                      251: "ru, kz, ge, 7da.kz, lemoney.kz",
                      252: "ru, kz, ge, 7da.kz, lemoney.kz",
                      253: "ru, kz, ge, 7da.kz, lemoney.kz",
                      254: "ru",
                      257: "ru, kz, ge, 7da.kz, lemoney.kz",
                      259: "ru, kz, ge, 7da.kz, lemoney.kz",
                      262: "leasing.kz",
                      263: "leasing.kz",
                      264: "leasing.kz",
                      265: "leasing.kz",
                      266: "ru, kz, ge, 7da.kz, lemoney.kz",
                      267: "ru",
                      271: "7da.kz, lemoney.kz",
                      272: "lemoney.kz",
                      273: "lemoney.kz",
                      274: "lemoney.kz",
                      275: "lemoney.kz",
                      276: "7da.kz, lemoney.kz",
                      279: "7da.kz, lemoney.kz",
                      283: "7da.kz, lemoney.kz",
                      }

COUNTRIES = {
    'ru': 'России', 'kz': 'Казахстана', 'ge': 'Грузии', 'leasing': 'Казахстана',
    "lemoney": 'Казахстана', '7da': 'Казахстана',
}
COUNTRIES_ABBR = {
    'России': 'ru', 'Казахстана': 'kz', 'Грузии': 'ge'
}

SYSTEM_USERS = {
    'ru': {
        '4slovo/finance': 'ru_finance',
        '4slovo/fs': 'fs4slovo',
        '4slovo.ru/chestnoe_slovo': 'f4slovo',
        '4slovo.ru/chestnoe_slovo_backend': 'crm4slovo',
        '4slovo.ru/chestnoe_slovo_landing': 'n4slovo',
        '4slovo.ru/api': 'api4slovo',
        '4slovo.ru/4slv': 'ru_4slv',
        'module/msm': '', 'docker/ru': '',
        '4slovo/finance_client': '', '4slovo/anonymize-replicator': '', 'docker/external_images': '',
        'docker/finance': '', 'docker/finance_client': '', '4slovo/anon-server': '', '4slovo/logging': '',
        '4slovo/expression': '', '4slovo.ru/common': '', '4slovo/common': '', '4slovo/sawmill': '', 'docker/ru-db': '',
        'docker/fias': '', '4slovo.ru/fias': '', 'docker/alpine-pkgs-repo': '', '4slovo.ru/osticket': '',
        "4slovo/short_link_client": '', '4slovo/mock-server': '', "4slovo/event-manager": '', "4slovo/cast-type": '',
        "4slovo/dto": '', '4slovo/reflection': '', '4slovo/csv': '', '4slovo/xxtea': '',
        '4slovo/cache': '', "4slovo/fs-client": '', "external/PHPExcel": '', 'module/message-sender-package': '',
        '4slovo/satis': 'satis', "4slovo/yaml-config": '', "4slovo/php-cs-fixer": '',
        "module/message-scheduler-module": '', "cards/card-info-recognizer": '', "4slovo/rabbitclient": '',
        "4slovo/interface-generator": '', "4slovo/money": '', "4slovo/registry-generator": '',
        '4slovo/enum-generator': '', "4slovo/timeservice_client": '', "4slovo/config": '', "docker/ru-db-v2": '',
        '4slovo/metrics-provider': '', '4slovo/S3Client': '', '4slovo/production-profiler': '',
        '4slovo/fias_client': '', '4slovo/test-coverage-checker': ''
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
        '4slovo/cache': '', "4slovo/fs-client": '', "external/PHPExcel": '', 'module/message-sender-package': '',
        '4slovo/php-cs-fixer': '', "module/message-scheduler-module": '', "cards/card-info-recognizer": '',
        "4slovo/rabbitclient": '', "4slovo/interface-generator": '', "4slovo/money": '',
        "4slovo/registry-generator": '', '4slovo/enum-generator': '', "4slovo/timeservice_client": '',
        "4slovo/config": '', "docker/ru-db-v2": ''
    },
    'kz': {
        '4slovo/finance': 'kz_finance', '4slovo/fs': 'kz_fs', '4slovo.kz/4slovokz': 'kz_f',
        '4slovo.kz/crm4slovokz': 'kz_backend_mfo', 'docker/kz': '', '4slovo/sumsub-client': '', 'sites/4slokz': '',
        'docker/kz-db': '', '4slovo.ru/4slv': '', 'docker/finance': '', 'docker/finance_client': '',
        '4slovo/mock-server': '', '4slovo/sawmill': '', '4slovo/S3Client': '', "4slovo/event-manager": '',
        "4slovo/cast-type": '', "4slovo/dto": '', '4slovo/reflection': '', '4slovo/csv': '', '4slovo/xxtea': '',
        '4slovo/cache': '', "4slovo/fs-client": '', "external/PHPExcel": '', "4slovo/config": '',
        '4slovo.ru/common': '', '7payda.kz/crm7paydakz': 'crm_paydak', '7payda.kz/7paydakz': 'f_paydakz',
        'docker/7paydakz': '', "cards/card-info-recognizer": '', "4slovo.kz/landing": 'kz_4slo',
        '4slovo/finance_client': ''
    },
    'kz2': {
        '4slovo/finance': 'kz_finance', '4slovo/fs': 'kz_fileshare', '4slovo.kz/4slovokz': 'kz_frontend',
        '4slovo.kz/crm4slovokz': 'kz_backend_mfo', 'docker/kz': '', '4slovo/sumsub-client': '', 'sites/4slokz': '',
        'docker/kz-db': '', '4slovo.ru/4slv': '', 'docker/finance': '', 'docker/finance_client': '',
        '4slovo/mock-server': '', '4slovo/sawmill': '', '4slovo/S3Client': '', "4slovo/event-manager": '',
        "4slovo/cast-type": '', "4slovo/dto": '', '4slovo/reflection': '', '4slovo/csv': '', '4slovo/xxtea': '',
        '4slovo/cache': '', "4slovo/fs-client": '', "external/PHPExcel": '', "4slovo/config": '',
        '4slovo.ru/common': '', "cards/card-info-recognizer": '', "4slovo.kz/landing": '', '4slovo/finance_client': ''
    }
}

MR_STATUS = {
    True: '(x) Конфликт!, ', False: '(/) Нет конфликтов, ',
    'can_be_merged': '(/) Нет конфликтов, ', 'cannot_be_merged': '(x) Конфликт!, ', 'unchecked': '(/) Нет конфликтов,',
    'cannot_be_merged_recheck': '(x) Конфликт!, ', 'checking': '(x) Конфликт!, ',
}
PRIORITY = {'Critical': '(*r) Critical', 'Highest': '(!) Highest', 'High': '(*) High', 'Medium': '(*g) Medium',
            'Low': '(*b) Low', 'Lowest': '(*b) Lowest', 'Критический': '(*r) Critical',
            'MEGA Critical': '(flag) MEGA Critical'}
PRIORITY_VALUE = {
    'MEGA Critical': 1, 'Critical': 2, 'Критический': 2, 'Highest': 3, 'High': 4, 'Medium': 5, 'Low': 6, 'Lowest': 7
}

# если надо собрать сборку, но не все задачи прошли тестирование, раскомментить ниже '] #' чтобы статусы стали доступны
STATUS_FOR_RELEASE = ['Released to production', 'Passed QA', 'In regression test', 'Ready for release',
                      'Закрыт', 'Fixed', 'Closed', 'Готово', 'In Regress Test RC'
                      ] # , 'Ready for review', 'Ready for technical solution review', 'In QA', 'Open', 'Ready for QA', 'In development', 'Reopened', 'Reviewing', 'Technical solution', 'В работе']
STATUS_READY = ['Released to production', 'Ready for release', 'Закрыт', 'Fixed', 'Closed']

STATUS_FOR_QA = ['Ready for QA', 'In QA']

TESTERS = {
    'm.pohilyj': 77,
    'a.melnik': 101,
    'e.evdokimov': 169,
}

PROJECTS_WITH_TESTS = [
    11, 20, 61, 62, 79, 93, 94, 97, 100, 110, 166, 172, 178, 187, 194, 201, 227, 245, 246, 247, 252, 259, 263, 264, 265,
    273, 274, 275, 276, 279
]
"""
        11: 4slovo.kz/crm4slovokz
        20: 4slovo.ru/chestnoe_slovo_backend
        61: 4slovo.ru/fias
        62: 4slovo.ru/chestnoe_slovo_landing
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
        245: 7payda.kz/crm7paydakz
        246: docker/7paydakz
        247: docker/7paydakz-db
        252: cards/card-info-recognizer
        259: 4slovo/satisfy
        263: 4slovo.kz/leasing/crm
        264: docker/leasing
        265: docker/leasing-db
        273: lemoney.kz/crmlemoneykz
        274: docker/lemoneykz
        275: docker/lemoney-db
        276: 4slovo/4slv
        279: 4slovo.ru/auto-rotate-document
"""
PROJECTS_WITHOUT_STAGING = [
    22, 86, 90, 91, 92, 103, 104, 113, 116, 119, 120, 121, 123, 124, 125, 135, 138, 139, 171, 178, 186, 194, 202, 204,
    207, 212, 215, 225, 227, 228, 229, 230, 231, 232, 233, 240, 242, 246, 247, 248, 251, 252, 253, 254, 257, 259, 264,
    265, 266, 271, 274, 275, 279, 283
]
"""
        90: 4slovo/sawmill
        91: 4slovo/common
        92: 4slovo/inn
        103: 4slovo/finance_client
        104: docker/finance_client
        113: 4slovo/rabbitclient
        116: 4slovo/fs-client
        119: 4slovo/yaml-config
        120: 4slovo/money
        121: 4slovo/enum-generator
        123: 4slovo/registry-generator
        124: 4slovo/interface-generator
        125: 4slovo/expression
        135: 4slovo/logging
        138: 4slovo/timeservice
        139: 4slovo/timeservice_client
        171: docker/kz-db
        178: 4slovo/anonymize-replicator
        186: module/message-sender-package
        194: 4slovo/anon-server
        202: module/rabbitmq
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
        257: 4slovo/metrics-provider
        259: 4slovo/satisfy
        264: docker/leasing
        265: docker/leasing-db
        266: 4slovo/db2confluence
        271: 4slovo/fias_client
        274: docker/lemoneykz
        275: docker/lemoney-db
        279: 4slovo.ru/auto-rotate-document
"""
DOCKER_PROJECTS = [94, 97, 100, 110, 166, 167, 172, 201, 246, 247, 264, 265, 274, 275, 276, 279]
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
        264: docker/leasing
        265: docker/leasing-db
        274: docker/lemoneykz
        275: docker/lemoney-db
        276: 4slovo/4slv
        279: 4slovo.ru/auto-rotate-document
"""

# DOMAIN = '4slovo.ru'
DOMAIN = '7pd.kz'
GIT_LAB = 'https://gitlab'
GIT_LAB_SERVER = f'https://gitlab.{DOMAIN}/'
ISSUE_URL = f'https://jira.{DOMAIN}/browse/'
JIRA_SERVER = f'https://jira.{DOMAIN}/'
JIRA_OPTIONS = {'server': JIRA_SERVER}
CONFLUENCE_SERVER = f"https://confluence.{DOMAIN}/"

CONFLUENCE_LINK = "https://confluence.{}/pages/viewpage.action?pageId={}"
MR_BY_IID = 'https://gitlab.{}/api/v4/projects/{}/merge_requests?iids[]={}&{}&"with_merge_status_recheck"=True'
RELEASE_ISSUES_URL = 'https://jira.{}/rest/api/latest/search?jql=fixVersion={}'
RELEASE_URL = 'https://jira.{}/projects/SLOV/versions/{}'
REMOTE_LINK = 'https://jira.{}/rest/api/latest/issue/{}/remotelink'

SMTP_PORT = 587
SMTP_SERVER = f'mail.{DOMAIN}'

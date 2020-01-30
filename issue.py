from build_task import config, message, release
from send_notifications import RELEASE_URL

issue = f'{{"fields": {{"fixVersions": [{{"self": "{RELEASE_URL.format(release['id'])}", "id": "{release['id']}", "description": "", "name": "{release['name']}", "archived": false, "released": false' \
f'}}],"priority": {{"self": "https://jira.4slovo.ru/rest/api/2/priority/2", "iconUrl": "https://jira.4slovo.ru/images/icons/priorities/high.svg", "name": "High","id": "2"' \
f'}},"assignee": {{"self": "https://jira.4slovo.ru/rest/api/2/user?username=a.dobrynin","name": "a.dobrynin","key": "a.dobrynin","emailAddress": "a.dobrynin@4slovo.ru","avatarUrls": {{' \
f'"48x48": "https://jira.4slovo.ru/secure/useravatar?ownerId=a.dobrynin&avatarId=10905",' \
f'"24x24": "https://jira.4slovo.ru/secure/useravatar?size=small&ownerId=a.dobrynin&avatarId=10905",' \
f'"16x16": "https://jira.4slovo.ru/secure/useravatar?size=xsmall&ownerId=a.dobrynin&avatarId=10905",' \
f'"32x32": "https://jira.4slovo.ru/secure/useravatar?size=medium&ownerId=a.dobrynin&avatarId=10905"}},"displayName": "Алексей А. Добрынин","active": true,"timeZone": "Europe/Moscow"' \
f'}},"status": {{"self": "https://jira.4slovo.ru/rest/api/2/status/1","description": "Проблема открыта. Ответственное лицо может начать работу по нему.",' \
f'"iconUrl": "https://jira.4slovo.ru/images/icons/statuses/open.png","name": "Открытый","id": "1","statusCategory": {{' \
f'"self": "https://jira.4slovo.ru/rest/api/2/statuscategory/2","id": 2,"key": "new","colorName": "blue-gray","name": "К выполнению"}}' \
f'}},"creator": {{"self": "https://jira.4slovo.ru/rest/api/2/user?username={config['user_data']['login']}","name": "{config['user_data']['login']}",' \
f'"key": "{config['user_data']['login']}","emailAddress": "{config['user_data']['login']}@4slovo.ru","avatarUrls": {{' \
f'"48x48": "https://jira.4slovo.ru/secure/useravatar?ownerId={config['user_data']['login']}&avatarId=12802",' \
f'"24x24": "https://jira.4slovo.ru/secure/useravatar?size=small&ownerId={config['user_data']['login']}&avatarId=12802",' \
f'"16x16": "https://jira.4slovo.ru/secure/useravatar?size=xsmall&ownerId={config['user_data']['login']}&avatarId=12802",' \
f'"32x32": "https://jira.4slovo.ru/secure/useravatar?size=medium&ownerId={config['user_data']['login']}&avatarId=12802"}},' \
f'"displayName": "{config['user_data']['login']}","active": true,"timeZone": "Europe/Moscow"},"subtasks": [],"reporter": {{' \
f'"self": "https://jira.4slovo.ru/rest/api/2/user?username={config['user_data']['login']}","name": "{config['user_data']['login']}",' \
f'"key": "{config['user_data']['login']}","emailAddress": "{config['user_data']['login']}@4slovo.ru","avatarUrls": {{' \
f'"48x48": "https://jira.4slovo.ru/secure/useravatar?ownerId={config['user_data']['login']}&avatarId=12802",' \
f'"24x24": "https://jira.4slovo.ru/secure/useravatar?size=small&ownerId={config['user_data']['login']}&avatarId=12802",' \
f'"16x16": "https://jira.4slovo.ru/secure/useravatar?size=xsmall&ownerId={config['user_data']['login']}&avatarId=12802",' \
f'"32x32": "https://jira.4slovo.ru/secure/useravatar?size=medium&ownerId={config['user_data']['login']}&avatarId=12802"' \
f'}},"displayName": "{config['user_data']['login']}","active": true,"timeZone": "Europe/Moscow"}},"aggregateprogress": {"progress": 0,"total": 0'\
f'}},"issuetype": {{"self": "https://jira.4slovo.ru/rest/api/2/issuetype/10002","id": "10002","description": "Задание для выполнения.",'\
f'"iconUrl": "https://jira.4slovo.ru/secure/viewavatar?size=xsmall&avatarId=10318&avatarType=issuetype","name": "Задача","subtask": false,"avatarId": 10318'\
f'}}, "timespent": null,"project": {{"self": "https://jira.4slovo.ru/rest/api/2/project/10000","id": "10000","key": "SLOV","name": "4Slovo",'\
f'"projectTypeKey": "software","avatarUrls": {{"48x48": "https://jira.4slovo.ru/secure/projectavatar?pid=10000&avatarId=10011",'\
f'"24x24": "https://jira.4slovo.ru/secure/projectavatar?size=small&pid=10000&avatarId=10011",'\
f'"16x16": "https://jira.4slovo.ru/secure/projectavatar?size=xsmall&pid=10000&avatarId=10011",'\
f'"32x32": "https://jira.4slovo.ru/secure/projectavatar?size=medium&pid=10000&avatarId=10011"}}'\
f'}},"description": "{message}","summary": "Сборка {release['name']}","comment": {{"comments": [],"maxResults": 0,"total": 0,"startAt": 0}}}}}}'
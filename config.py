TOKEN = '1101033060:AAGqkBebKtcdg-0uJcYlmgjWrGlCniVT8Fo'
#Подключение к бд
DB_ADDRESS = "127.0.0.1"
DB_USER = 'root'
DB_PASSWORD = '13061911'
DB_BASE = 'green'
DB_CHARSET="utf8mb4"

#Необходимо для подключния к докам с локализацией
PATH_TO_JSON_FILE = "./PythonProject.json"
TABLE_ID = "1CjX0ME7KTsYVmTuxjdFKSbOg5fyKNrCHhCGSPKcm434"

#Max count of tables
TABLE_COUNTS = 35

#STATUS of reservs
ACTIVE = "active"
DELETED = 'deleted'
STOPED = 'stoped'
ENDED = 'ended'

#Admin password and command for login
PASSWORD = '147852'
ADMIN_COMMAND = 'login'

#Тут можно указать список тех, кому нужно присылать ежедневные отчеты в конце дня
#Указать можно одного пользователя в виде строки ("userName"), или списка пользователей ["usename1", 'userbname2]
#Пользователь должен быть рагерестрирован в боте
EXCELS_SEND_TO_USERS = 'ursyyy'
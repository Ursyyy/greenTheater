TOKEN = '1101033060:AAGqkBebKtcdg-0uJcYlmgjWrGlCniVT8Fo'
#Подключение к бд
DB_ADDRESS = "127.0.0.1"
DB_USER = 'root'
DB_PASSWORD = '13061911'
DB_BASE = 'green'
DB_CHARSET="utf8mb4"

#Необходимо для подключния к докам с локализацией
PATH_TO_JSON_FILE = "./pp.json"
#Id таблицы, в которую бадат записываться данные (береться из ссылки на таблицу)
TABLE_ID = "1CjX0ME7KTsYVmTuxjdFKSbOg5fyKNrCHhCGSPKcm434"

#Max count of tables
TABLE_COUNTS = 35

#STATUS of reservs
ACTIVE = "active"
DELETED = 'deleted'
STOPED = 'stoped'
ENDED = 'ended'

ADMINS_LIST = [{"phone_number": "+380961311333", "first_name": "Наташа", "user_id": 248199079},
{"phone_number": "+380971360490", "first_name": "Екатерина", "last_name": "Соловьева", "user_id": 231949160}
]

#Admin password and command for login
PASSWORD = '147852'
ADMIN_COMMAND = 'login'

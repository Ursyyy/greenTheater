import mysql.connector

from config import DB_ADDRESS, DB_BASE, DB_PASSWORD, DB_USER, DB_CHARSET

connector = mysql.connector.connect(
	host=DB_ADDRESS,
	user=DB_USER,
	password=DB_PASSWORD,
	database=DB_BASE,
	charset=DB_CHARSET
)

cursor = connector.cursor()

def connect() -> None:
	global connector
	global cursor
	if not connector.is_connected():
		connector = mysql.connector.connect(
			host=DB_ADDRESS,
			user=DB_USER,
			password=DB_PASSWORD,
			database=DB_BASE,
			charset=DB_CHARSET
		)
		cursor = connector.cursor()

def checkUser(tid: [int, str]) -> bool:
	try:
		cursor.execute('select username from users where telegramId = %s', (int(tid),))
		id = cursor.fetchone()
		return False if id is None else True
	except: return False

def addUser(tid:[int, str], tname:str, firstName: str, lastName: str, phone: str, commandName: str) -> None:
	cursor.execute('insert into users (telegramId, username, firstName, lastName, phone, commandName) values (%s, %s, %s, %s, %s, %s)', (int(tid), tname, firstName, lastName, phone, commandName))
	connector.commit()

def addReserv(): pass

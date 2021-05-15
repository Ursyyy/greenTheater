from typing import Union
import mysql.connector
from dates import getCurDay
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

def checkUser(tid: Union[int, str]) -> bool:
	try:
		cursor.execute('select username from users where telegramId = %s', (int(tid),))
		id = cursor.fetchone()
		return False if id is None else True
	except: return False

def addUser(tid:Union[int, str], tname:str, firstName: str, lastName: str, phone: str, commandName: str) -> None:
	cursor.execute('insert into users (telegramId, username, firstName, lastName, phone, commandName) values (%s, %s, %s, %s, %s, %s)', (int(tid), tname, firstName, lastName, phone, commandName))
	connector.commit()

def addReserv(tid: Union[int, str], reservTime: str, tablesCount: Union[int, str], comment:str=None) -> int: 
	createdId = None
	try:
		cursor.execute('insert into reservs (userId, createTime, reservTime, tablesCount, commentary) values (%s, %s, %s, %s, %s)', 
			(int(tid), getCurDay(), reservTime, int(tablesCount), comment))
	except: createdId = -1
	finally: return createdId 

def getUserReserv(tid: Union[int, str]) -> list:
	date = getCurDay()
	reservsList = []
	try:
		cursor.execute('select * from reservs where telegramId = %s and reservTime > %s', (tid, date))
	except: pass
	finally: pass
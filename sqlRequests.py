from typing import Union
import mysql.connector
from dates import getCurDay
from config import DB_ADDRESS, DB_BASE, DB_PASSWORD, DB_USER, DB_CHARSET, ACTIVE, STOPED, DELETED

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
	try:
		cursor.execute('insert into reservs (userId, createTime, reservTime, tablesCount, status, commentary) values (%s, %s, %s, %s, %s, %s)', 
			(int(tid), getCurDay(), reservTime, int(tablesCount), ACTIVE, comment))
		connector.commit()
		cursor.execute('select id from reservs where userId = %s and createTime = %s and reservTime = %s', (int(tid), getCurDay(), reservTime))
		createdId = cursor.fetchone()[0]
	except: createdId = -1
	finally: return createdId 

def checkDate(date: str) -> int:
	try: 
		cursor.execute('select tablesCount from reservs where reservTime = %s and status != %s', (date,DELETED))
		count = 0
		for item in cursor.fetchall():
			count += item[0]
	except: count = 0
	finally: return count 

def getUserReserv(tid: Union[int, str]) -> list:
	date = getCurDay()
	try:
		cursor.execute('select * from reservs where userId = %s and reservTime > %s and status = %s or status = %s', (tid, date, ACTIVE, STOPED))
		reservList = cursor.fetchall()
	except Exception as e: 
		print(e)
		reservList = []
	finally: return reservList

def removeReserv(reservId: Union[int, str]) -> bool:
	try:
		cursor.execute('update reservs set status = %s where id = %s', (DELETED ,int(reservId),))
		connector.commit()
		return True
	except Exception as e: 
		return False

def changeTime(reservId, newTime, tablesCount) -> bool:
	try:
		cursor.execute('update reservs set reservTime = %s, tablesCount = %s where id = %s', (str(newTime), int(reservId), int(tablesCount)))
		connector.commit()
		return True
	except Exception as e: 
		return False

def stopReserv(startTime: str, endTime: str) -> bool:
	try:
		cursor.execute('update reservs set status = %s where reservTime >= %s and reservTime <= %s', (STOPED, startTime, endTime))
		connector.commit()
		return True
	except: return False
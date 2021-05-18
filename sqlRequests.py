from typing import Union
import mysql.connector
from dates import getCurDay
from config import DB_ADDRESS, DB_BASE, DB_PASSWORD, DB_USER, DB_CHARSET, ACTIVE, STOPED, DELETED, ENDED

connector = mysql.connector.connect(
	host=DB_ADDRESS,
	user=DB_USER,
	password=DB_PASSWORD,
	database=DB_BASE,
	charset=DB_CHARSET
)

cursor = connector.cursor()

def connect(callback) -> None:
	def wrapper(*args):
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
		return callback(*args)
	return wrapper

@connect
def checkUser(tid: Union[int, str]) -> bool:
	try:
		cursor.execute('select username from users where telegramId = %s', (int(tid),))
		id = cursor.fetchone()
		return False if id is None else True
	except: return False
@connect
def addUser(tid:Union[int, str], tname:str, firstName: str, lastName: str, phone: str, commandName: str) -> None:
	cursor.execute('insert into users (telegramId, username, firstName, lastName, phone, commandName) values (%s, %s, %s, %s, %s, %s)', (int(tid), tname, firstName, lastName, phone, commandName))
	connector.commit()
@connect
def getUser(username: str) -> int:
	cursor.execute('select telegramId from users where username = %s', (username, ))
	result = cursor.fetchone()
	if result is None: return -1
	return result[0]
@connect
def addReserv(tid: Union[int, str], reservTime: str, tablesCount: Union[int, str], comment:str=None) -> int: 
	try:
		cursor.execute('select id from stoppedReservs where startTime <= %s and endTime > %s', (reservTime, reservTime))
		stop = cursor.fetchone()
		if not stop is None: 
			createdId = -2
			return
		cursor.execute('insert into reservs (userId, createTime, reservTime, tablesCount, status, commentary) values (%s, %s, %s, %s, %s, %s)', 
			(int(tid), getCurDay(), reservTime, int(tablesCount), ACTIVE, comment))
		connector.commit()
		cursor.execute('select id from reservs where userId = %s and createTime = %s and reservTime = %s', (int(tid), getCurDay(), reservTime))
		createdId = cursor.fetchone()[0]
	except: createdId = -1
	finally: return createdId 
@connect
def checkDate(date: str) -> int:
	try: 
		cursor.execute('select tablesCount from reservs where reservTime = %s and status != %s', (date,DELETED))
		count = 0
		for item in cursor.fetchall():
			count += item[0]
	except: count = 0
	finally: return count 
@connect
def getUserReserv(tid: Union[int, str]) -> list:
	date = getCurDay()
	try:
		
		cursor.execute('select * from reservs where userId = %s and reservTime > %s and (status = %s or status = %s)', (tid, date, ACTIVE, STOPED))
		print(cursor.description)
		reservList = cursor.fetchall()
		print(reservList)
	except Exception as e: 
		print(e)
		reservList = []
	finally: return reservList
@connect
def removeReserv(reservId: Union[int, str]) -> bool:
	try:
		cursor.execute('update reservs set status = %s where id = %s', (DELETED ,int(reservId),))
		connector.commit()
		return True
	except Exception as e: 
		return False
@connect
def changeTime(reservId, newTime, tablesCount) -> int:
	try:
		cursor.execute('select id from stoppedReservs where startTime >= %s and endTime < %s', (newTime,))
		stop = cursor.fetchone()
		if not stop is None: 
			return -1
		cursor.execute('update reservs set reservTime = %s, tablesCount = %s where id = %s', (str(newTime), int(reservId), int(tablesCount)))
		connector.commit()
		return 1
	except: return 0
@connect
def stopReserv(startTime: str, endTime: str) -> bool:
	try:
		cursor.execute('update reservs set status = %s where reservTime >= %s and reservTime <= %s', (STOPED, startTime, endTime))
		connector.commit()
		cursor.execute('insert into stoppedReservs (startTime, endTime) values (%s, %s)', (startTime, endTime))
		connector.commit()
		return True
	except: return False
@connect
def getDailyReserv(startTime: str, endTime: str):
	try:
		cursor.execute('select distinct userId from reservs where reservTime >= %s and reservTime <= %s and status = %s' , (startTime, endTime, ACTIVE))
		users = cursor.fetchall()
		if users == []: return []
		reservList = []
		for user in users:
			cursor.execute('select id, reservTime, tablesCount, status from reservs where reservTime >= %s and reservTime <= %s and userId = %s and status = %s', (startTime, endTime, int(user[0]), ACTIVE))
			reservList.append({
				'user': int(user[0]),
				'list': cursor.fetchall()
			})
		return reservList
	except Exception as e: 
		print(e)
		return []

@connect
def fetchTableData(date):
	cursor.execute('select * from users')
	users_header = [row[0] for row in cursor.description]
	users = {}
	users_rows = []
	for i in cursor.fetchall():
		users_rows.append(i)
		users[i[0]] = i[1]
	cursor.execute('select * from reservs where status != %s', (ENDED, ))
	reserv_header = [row[0] for row in cursor.description]
	reserv_data = cursor.fetchall()
	reserv_rows = []
	for i in reserv_data:
		row = [str(j) if count != 1 else users[int(j)] for count, j in enumerate(i) ]
		reserv_rows.append(row)
	cursor.execute('update reservs set status = %s where reservTime < %s', (ENDED, date))
	connector.commit()
	return [reserv_header, reserv_rows], [users_header, users_rows]

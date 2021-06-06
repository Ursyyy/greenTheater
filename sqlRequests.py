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
def getAllUsers() -> list:
	try:
		cursor.execute('select telegramId from users')
		usersList = [item[0] for item in cursor.fetchall()]
	except: usersList = []
	finally: return usersList

@connect
def getUsersForSheets() -> list:
	try:
		cursor.execute('''
			select concat(firstName, " ", lastName), commandName, phone, username
			from users
		''')
		return cursor.fetchall()
	except: return []

@connect
def getUser(username: str) -> int:
	cursor.execute('select telegramId from users where username = %s', (username, ))
	result = cursor.fetchone()
	if result is None: return -1
	return result[0]
@connect
def addReserv(tid: Union[int, str], reservTime: str, endTime:str, tablesCount: Union[int, str], comment:str=None) -> int: 
	try:
		cursor.execute('select id from stoppedReservs where startTime <= %s and endTime > %s', (reservTime, endTime))
		stop = cursor.fetchone()
		if not stop is None: 
			createdId = -2
			return
		cursor.execute('insert into reservs (userId, createTime, reservTime, endTime, tablesCount, status, commentary) values (%s, %s, %s, %s, %s, %s, %s)', 
			(int(tid), getCurDay(), reservTime, endTime, int(tablesCount), ACTIVE, comment))
		connector.commit()
		cursor.execute('select id from reservs where userId = %s and createTime = %s and reservTime = %s', (int(tid), getCurDay(), reservTime))
		createdId = cursor.fetchone()[0]
	except Exception as e: 
		print(e)
		createdId = -1
	finally: return createdId 

@connect
def checkDate(startTime: str, endTime: str) -> int:
	try: 
		cursor.execute('''
			select sum(tablesCount) from reservs 
			where cast(%s as datetime) between cast(reservTime as DATETIME) and cast(endTime as datetime)
			and cast(%s as datetime) between cast(reservTime as DATETIME) and cast(endTime as datetime)
			and status != %s
		''', (startTime, endTime,DELETED))
		count = cursor.fetchone()[0]
		count = 0 if count is None else count
	except: count = 0
	finally: return count

@connect 
def getUsersByReservTime(reservTime: str) -> list:
	try:
		cursor.execute("""
		select concat(users.firstName, " ",users.lastName, " (",users.commandName, ")")
		from reservs
		inner join users
		on reservs.userId = users.telegramId
		where cast(%s as datetime) between cast(reservs.reservTime as DATETIME) and cast(reservs.endTime as datetime)
		and reservs.status != %s
		""", (reservTime, DELETED))
		return [item[0] for item in cursor.fetchall()]
	except: return []

@connect
def getReservedTablesAtTime(startTime: str, endTime: str) -> int:
	try:
		cursor.execute("""
		select sum(tablesCount)
		from reservs
		where cast(%s as datetime) and cast(%s as datetime) between cast(reservTime as DATETIME) and cast(endTime as datetime)
		and status != %s
		""", (startTime, endTime, DELETED))
		return int(cursor.fetchone()[0])
	except: return 0



@connect
def getUserReserv(tid: Union[int, str]) -> list:
	date = getCurDay()
	try:
		cursor.execute('select * from reservs where userId = %s and reservTime >= %s and (status = %s or status = %s)', (tid, date, ACTIVE, STOPED))
		reservList = cursor.fetchall()
	except: reservList = []
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
def changeTime(reservId, newTime, endTime, tablesCount) -> int:
	try:
		cursor.execute('select id from stoppedReservs where startTime >= %s and endTime < %s', (newTime, newTime))
		stop = cursor.fetchone()
		if not stop is None: 
			return -1
		cursor.execute('update reservs set reservTime = %s, endTime = %s, tablesCount = %s, status = %s where id = %s', (str(newTime), str(endTime),int(tablesCount), int(reservId), ACTIVE))
		connector.commit()
		return 1
	except Exception as e: 
		print(e)
		return 0

@connect
def stopReserv(startTime: str, endTime: str, description:str=None) -> bool:
	try:
		#
		#
		#
		cursor.execute('update reservs set status = %s where reservTime >= %s and endTime <= %s', (STOPED, startTime, endTime))
		connector.commit()
		cursor.execute('insert into stoppedReservs (startTime, endTime, description) values (%s, %s, %s)', (startTime, endTime, description))
		connector.commit()
		return True
	except: return False

@connect
def getWorkloadByDate(date: str) -> list:
	resultList = []
	try:
		cursor.execute('''
		select reservs.reservTime, reservs.endTime, reservs.tablesCount, users.firstName, users.lastName, users.phone, users.commandName
		from reservs
		inner join users
		on reservs.userId = users.telegramId
		where reservTime > %s and reservTime < %s
		order by reservTime
		''', (f"{date} 09:00:00", f"{date} 19:00:00"))
		resultList = cursor.fetchall()
	except: resultList = []
	finally: return resultList

@connect
def getStopsReserv() -> list:
	try:
		cursor.execute('select startTime, endTime, description from stoppedReservs where startTime > %s', (getCurDay(), ))
		stopsList = cursor.fetchall()
	except: stopsList = []
	finally: return stopsList

@connect
def getDailyReserv(startTime: str, endTime: str):
	try:
		cursor.execute('select distinct userId from reservs where reservTime >= %s and endTime <= %s and status = %s' , (startTime, endTime, ACTIVE))
		users = cursor.fetchall()
		if users == []: return []
		reservList = []
		for user in users:
			cursor.execute('select id, reservTime, tablesCount, status from reservs where reservTime >= %s and endTime <= %s and userId = %s and status = %s', (startTime, endTime, int(user[0]), ACTIVE))
			reservList.append({
				'user': int(user[0]),
				'list': cursor.fetchall()
			})
		return reservList
	except: return []
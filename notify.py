from aiocron import crontab
from bot import bot
from dates import getCurDay, getDaysForNotify, getDayForHourNotify, getDay, START_HOUR
from sqlRequests import getDailyReserv, getUsersByReservTime, getReservedTablesAtTime, getUsersForSheets
from sheets import WriteDataToSheets, WriteUsers
from config import ACTIVE, TABLE_COUNTS
from keyboards import getReservKB

@crontab("0 9 * * *")
async def dailyMailing():
	today = getDaysForNotify()
	usersReservs = getDailyReserv(*today)
	for item in usersReservs:
		text = "Завтра у вас запланорованно бронирование:" if len(item['list']) == 1 else "Завтра у вас запланорованны бронирования"
		await bot.send_message(chat_id=item['user'], text=text)
		for reserv in item['list']:
			time = str(reserv[1]).split()[1][:5]
			endTime = int(time[:2]) + 1
			status = 'активна' if reserv[-1] == ACTIVE else 'остановлена'
			text = f"Бронь на {getDay(str(reserv[1]).split()[0])}\nВремя: {time}-{endTime}:00\nКол-во столов: {reserv[-2]}\nСтатус: {status}"
			await bot.send_message(chat_id=item['user'], text=text, reply_markup=getReservKB(reserv[0]))


@crontab('0 9-17 * * *')
async def hourlyMailing():
	today = getDayForHourNotify()
	usersReservs = getDailyReserv(*today)
	for item in usersReservs:
		await bot.send_message(chat_id=item['user'], text="Через час у вас запланировано следующее броноравние:")
		for reserv in item['list']:
			time = str(reserv[1]).split()[1][:5]
			endTime = int(time[:2]) + 1
			status = 'активна' if reserv[-1] == ACTIVE else 'остановлена'
			text = f"Бронь на {getDay(str(reserv[1]).split()[0])}\nВремя: {time}-{endTime}:00\nКол-во столов: {reserv[-2]}\nСтатус: {status}"
			await bot.send_message(chat_id=item['user'], text=text, reply_markup=getReservKB(reserv[0]))

async def saveToSheets():
	date = getCurDay().split()[0]
	resultList = []
	for hour in START_HOUR:
		users = ', '.join(getUsersByReservTime(f"{date} {hour}:00:00"))
		tablesCount = getReservedTablesAtTime(f"{date} {hour}:00:00", f"{date} {hour}:59:59")
		resultList.append([date, f'{hour}:00 - {hour + 1}:00', tablesCount, TABLE_COUNTS - tablesCount, users])
	try:
		WriteDataToSheets(date, resultList)
	except Exception as e: print(e)
	try:
		WriteUsers(getUsersForSheets())
	except: pass

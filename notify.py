import aiocron
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from bot import dp, bot
from os import remove
from dates import getDaysForNotify, getDayForHourNotify, getCurDay, getDay
from sqlRequests import getDailyReserv, getUser
from config import EXCELS_SEND_TO_USERS
from keyboards import getReservKB
from exportToExcel import export

@aiocron.crontab("0 9 * * *")
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


@aiocron.crontab('0 9-17 * * *')
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

# @aiocron.crontab('0 19 * * *')
async def dailyReport():
	day = getCurDay().split()[0]
	export(day)
	usersToSend = EXCELS_SEND_TO_USERS
	if type(usersToSend) is str: usersToSend = [usersToSend]
	with open('./excels/' + day + '.xlsx', 'rb') as doc:
		for user in usersToSend:
			userId = getUser(user)
			if userId == -1: return
			await bot.send_document(userId, doc, caption=f"Отчет за сегодня({day})")
	remove('./excels/' + day + '.xlsx')
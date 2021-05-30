from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import message
from bot import bot, dp
from keyboards import getReservKB
from dates import getDays, getDay, HOURS, getStartHours, getEndHours
from sqlRequests import addReserv, checkDate, removeReserv, changeTime
from config import TABLE_COUNTS

RESERV_CALLBACKS = ['check_date', 'back_to_dates', 'cancel', 'set_start_time', 'set_end_time', 'table_count', 'create_reserv',
					'reserv_cancel', 'transfer_reserv', 'reserv_all_day']
	
def checkReservCallbacks(data):
	flag = False
	if data in RESERV_CALLBACKS: flag = True
	if data.split('=')[0] in RESERV_CALLBACKS and not flag: flag = True
	return flag 


@dp.callback_query_handler(lambda c: checkReservCallbacks(c.data))
async def ReservHandler(cd: types.CallbackQuery, state: FSMContext):
	if cd.data.startswith('check_date'):
		date, isReserv = cd.data.split('=')[1:]
		async with state.proxy() as data: 
			data['date'] = date
			data['isReserv'] = True if isReserv == 'reserv' else False
		day = getDay(date)
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in getStartHours(date): 
			keyboard.add(types.InlineKeyboardButton(text=f"{item}:00", callback_data=f"set_start_time={item}"))
		keyboard.add(types.InlineKeyboardButton(text="Весь день", callback_data='reserv_all_day'))
		keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data="back_to_dates"))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выбранный день: {day}\nВыберите время брони:", reply_markup=keyboard)

	elif cd.data.startswith('back_to_dates'):
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		dates = getDays()
		for item in dates:
			keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"check_date={item['dayStamp']}"))
		keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выберите день:", reply_markup=keyboard)

	elif cd.data.startswith('cancel'):
		await state.finish()
		await bot.delete_message(cd.from_user.id, cd.message.message_id)

	elif cd.data.startswith('set_start_time'):
		startTime = cd.data.split('=')[1]
		async with state.proxy() as data: 
			data['start_time'] = startTime
			date = data['date']
		day = getDay(date)
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in getEndHours(int(startTime)): 
			count = TABLE_COUNTS - checkDate(f"{date} {startTime}:00:00", f"{date} {item}:00:00")
			if count > 0: callback = f"set_end_time={item}={count}"
			else: callback = "pass"
			keyboard.add(types.InlineKeyboardButton(text=f"{item}:00 ({count} мест свободно)", callback_data=callback))
		keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=f"check_date={date}"))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выбранный день: {day}\nВыберите конечное время брони:", reply_markup=keyboard)


	elif cd.data.startswith('set_end_time'):
		_, time, count = cd.data.split('=')
		count = int(count)
		async with state.proxy() as data: data['end_time'] = time
		twoTables = 'table_count=2' if count > 1 else "pass"
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton(text='1 место', callback_data='table_count=1'),
			types.InlineKeyboardButton(text='2 местa', callback_data=twoTables),
			types.InlineKeyboardButton(text='Больше 2-х мест', callback_data='table_count=-1'),
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Сколько мест вам нужно?\nМест сободно: {count}", reply_markup=keyboard)

	elif cd.data.startswith('reserv_all_day'):
		async with state.proxy() as data:
			data['start_time'] = 10
			data['end_time'] = 18
		count = 2
		twoTables = 'table_count=2' if count > 1 else "pass"
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton(text='1 место', callback_data='table_count=1'),
			types.InlineKeyboardButton(text='2 местa', callback_data=twoTables),
			types.InlineKeyboardButton(text='Больше 2-х мест', callback_data='table_count=-1'),
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Сколько мест вам нужно?\nМест сободно: {count}", reply_markup=keyboard)


	elif cd.data.startswith('table_count'):
		count = int(cd.data.split('=')[1])
		if count == -1: 
			await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Для заказа более 2-х столов вам необходимо связаться с администратором" )
			return
		async with state.proxy() as data: 
			data['count'] = count
			startTime = data['start_time']
			endTime = data['end_time']
			date = getDay(data['date'])
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton(text='Подтвердить', callback_data='create_reserv'),
			types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выбранные данные:\nДата: {date}\nВремя: {startTime}:00 - {endTime}:00\nКол-во мест: {count}", reply_markup=keyboard)

	elif cd.data.startswith('create_reserv'):
		async with state.proxy() as data: 
			isReserv = data['isReserv']
			count = data['count']
			startTime = data['start_time']
			endTime = data['end_time']
			date = data['date']
		if isReserv:
			reversId = addReserv(cd.from_user.id, f"{date} {startTime}:00", f"{date} {endTime}:00", count)
			if reversId >= 0:
				await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Вжууух! Время коworkать! Бронь успешно создана. А значит, рабочее open-air место {getDay(date)} с {startTime}:00 по {endTime}:00 ждет тебя в Зелёном театре.", reply_markup=getReservKB(reversId))
			elif reversId == -1: await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Возникла ошибка при бронировании, обратитесь к администратору за помощью")
			elif reversId == -2: await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="В это время создание бронирования заблокирования, обратитесь к администратору за сведеньями")
		else:
			async with state.proxy() as data: reservId = data['id']
			status = changeTime(reservId, f"{date} {startTime}:00", f"{date} {endTime}:00", count)
			if status == 1: await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Время бронирования перенесено!\n Рабочее open-air место{getDay(date)} с {startTime}:00 по {endTime}:00 ждет тебя в Зелёном театре.", reply_markup=getReservKB(reservId))
			elif status == 0: await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Возникла ошибка при бронировании, обратитесь к администратору за помощью")
			elif status == -1: await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="В это время создание бронирования заблокирования, обратитесь к администратору за сведеньями")


	elif cd.data.startswith('reserv_cancel'):
		reservId = cd.data.split('=')[1]
		if removeReserv(reservId): mesText = "Бронь отменена"
		else: mesText = "Что-то пошло не так"
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=mesText)
	
	elif cd.data.startswith('transfer_reserv'):
		reservId = cd.data.split('=')[1]
		async with state.proxy() as data: data['id'] = reservId
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		dates = getDays()
		for item in dates:
			keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"check_date={item['dayStamp']}=transfer"))
		keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Выберите день:", reply_markup=keyboard)
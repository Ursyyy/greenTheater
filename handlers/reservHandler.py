from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import message
from bot import bot, dp
from keyboards import getReservKB
from dates import getDays, getDay, HOURS
from sqlRequests import addReserv, checkDate, removeReserv, changeTime
from config import TABLE_COUNTS

RESERV_CALLBACKS = ['check_date', 'back_to_dates', 'cancel', 'set_time', 'table_count', 'create_reserv',
					'reserv_cancel', 'transfer_reserv', 'transfer_date', 'transfer_time', 'transfer_table_count']
	
def checkReservCallbacks(data):
	flag = False
	if data in RESERV_CALLBACKS: flag = True
	if data.split('=')[0] in RESERV_CALLBACKS and not flag: flag = True
	return flag 


@dp.callback_query_handler(lambda c: checkReservCallbacks(c.data))
async def ReservHandler(cd: types.CallbackQuery, state: FSMContext):
	if cd.data.startswith('check_date'):
		date = cd.data.split('=')[1]
		async with state.proxy() as data: data['date'] = date
		day = getDay(date)
		#По дате выборка из бд
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in HOURS: 
			count = TABLE_COUNTS - checkDate(f"{date} {item.split('-')[0]}:00")
			if count > 0: callback = f"set_time={item.split()[0]}={count}"
			else: callback = "pass"
			keyboard.add(types.InlineKeyboardButton(text=item.replace('count', str(count)), callback_data=callback))
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
		await bot.delete_message(cd.from_user.id, cd.message.message_id)

	elif cd.data.startswith('set_time'):
		text, time, count = cd.data.split('=')
		count = int(count)
		async with state.proxy() as data: data['time'] = time
		twoTables = 'table_count=2' if count > 1 else "pass"
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton(text='1 место', callback_data='table_count=1'),
			types.InlineKeyboardButton(text='2 местa', callback_data=twoTables),
			types.InlineKeyboardButton(text='Больше 2-х мест', callback_data='table_count=-1'),
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Сколько мест вам нужно?", reply_markup=keyboard)

	elif cd.data.startswith('table_count'):
		count = int(cd.data.split('=')[1])
		if count == -1: 
			await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Для заказа более 2-х столов вам необходимо связаться с администратором" )
			return
		async with state.proxy() as data: 
			data['count'] = count
			time = data['time']
			date = getDay(data['date'])
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton(text='Подтвердить', callback_data='create_reserv'),
			types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выбранные данные:\nДата: {date}\nВремя: {time}\nКол-во мест: {count}", reply_markup=keyboard)

	elif cd.data.startswith('create_reserv'):
		async with state.proxy() as data: 
			count = data['count']
			time = data['time']
			date = data['date']
		reversId = addReserv(cd.from_user.id, f"{date} {time.split('-')[0]}:00", count)
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Бронь успешно создана!\n{getDay(date)} {time}\nВаше рабочее место в Зеленом театре ждет вас", reply_markup=getReservKB(reversId))

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
			keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"transfer_date={item['dayStamp']}"))
		keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Выберите день:", reply_markup=keyboard)

	elif cd.data.startswith('transfer_date'):
		date = cd.data.split('=')[1]
		async with state.proxy() as data: data['date'] = date
		day = getDay(date)
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in HOURS: 
			count = TABLE_COUNTS - checkDate(f"{date} {item.split('-')[0]}:00")
			if count > 0: callback = f"transfet_time={item.split()[0]}={count}"
			else: callback = "pass"
			keyboard.add(types.InlineKeyboardButton(text=item.replace('count', str(count)), callback_data=callback))
		for item in HOURS: keyboard.add(types.InlineKeyboardButton(text=item.replace('count', '35'), callback_data=callback))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выбранный день: {day}\nВыберите время брони:", reply_markup=keyboard)

	elif cd.data.startswith('transfer_time'): 
		text, time, count = cd.data.split('=')
		count = int(count)
		async with state.proxy() as data: data['time'] = time
		twoTables = 'transfer_table_count=2' if count > 1 else "pass"
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton(text='1 место', callback_data='transfer_table_count=1'),
			types.InlineKeyboardButton(text='2 местa', callback_data=twoTables),
			types.InlineKeyboardButton(text='Больше 2-х мест', callback_data='table_count=-1'),
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Сколько мест вам нужно?", reply_markup=keyboard)

	elif cd.data.startswith('transfer_table_count'):
		count = cd.data.split('=')[1]
		async with state.proxy() as data: 
			reservId = data['id']
			time = data['time']
			date = data['date']
		if changeTime(reservId, f"{date} {time.split('-')[0]}:00", count):	await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Время бронирования перенесено!\n{getDay(date)} {time}\nВаше рабочее место в Зеленом театре ждет вас", reply_markup=getReservKB(reservId))
		else: await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Что-то пошло не так")

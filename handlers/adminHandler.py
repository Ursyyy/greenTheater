from aiogram.dispatcher import FSMContext
from aiogram import types
from bot import bot, dp
from keyboards import getReservKB
from dates import getDays, START_HOUR, END_HOUR, getDay, HOURS
from sqlRequests import stopReserv, checkDate, getUser
from state_machine import Admin
from config import PASSWORD, ADMIN_COMMAND, TABLE_COUNTS


@dp.message_handler(commands=[ADMIN_COMMAND])
async def adminLogin(message: types.Message): 
	await message.answer("Введите пароль для подтверждения личности:")
	await Admin.password.set()

@dp.message_handler(state=Admin.setUser)
async def setUserName(message: types.Message, state: FSMContext):
	username = message.text
	if username.startswith('@'): username = username[1:]
	async with state.proxy() as data: data['user'] = getUser(username)
	keyboard = types.InlineKeyboardMarkup(row_width=1)
	for item in getDays():
		keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"admin_date_reserv={item['dayStamp']}"))
	keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
	await state.finish()
	await message.answer(text="Выберите день для бронирования:", reply_markup=keyboard)

@dp.message_handler(state=Admin.password)
async def adminPass(message: types.Message, state: FSMContext):
	answer = message.text
	if answer == PASSWORD:
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton('Отменить бронирования определенного дня', callback_data="admin_cancel_reserv"),
			types.InlineKeyboardButton('Забронировать', callback_data='admin_reserv'),
			types.InlineKeyboardButton('Выход', callback_data='admin_exit')
		])
		await message.answer('Вы открыли панель администратора', reply_markup=keyboard)
	else: await message.answer('Пароль не верный, свяжитесь с администратором для уточнения пароля')
	await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('admin'))
async def adminCallbacks(cd: types.CallbackQuery, state: FSMContext):
	if cd.data.startswith('admin_cancel_reserv'):
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in getDays():
			keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"admin_cancel_date={item['dayStamp']}"))
		keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Выберите день для отмены бронирований:", reply_markup=keyboard)

	elif cd.data.startswith('admin_cancel_date'):
		date = cd.data.split('=')[1]
		async with state.proxy() as data: data['date'] = date
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in START_HOUR:	keyboard.add(types.InlineKeyboardButton(text=f"{item}:00", callback_data=f'admin_cancel_start_time={item}'))
		keyboard.add(types.InlineKeyboardButton('Весь день', callback_data='admin_cancel_all_day'))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выбранный день: {getDay(date)}\nВыберите с какого вренени отенить бронирования:", reply_markup=keyboard)

	elif cd.data.startswith('admin_cancel_start_time'): 
		time = cd.data.split('=')[1]
		async with state.proxy() as data: data['time'] = time
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		keyboard.add(*[types.InlineKeyboardButton(text=f"{item}:00", callback_data=f'admin_cancel_end_time={item}') for item in END_HOUR if item > int(time)])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выберите по какое время отенить бронирования:", reply_markup=keyboard)

	elif cd.data.startswith('admin_cancel_all_day') or cd.data.startswith('admin_cancel_end_time'): 
		async with state.proxy() as data: 
			date = data['date']
			if cd.data.startswith('admin_cancel_end_time'):
				data['start time'] = f"{date} {data['time']}:00"
				data['end time'] = end_time = f"{date} {cd.data.split('=')[1]}:00"
				start_time, end_time= f"{data['time']}:00", f"{cd.data.split('=')[1]}:00"
			else:
				data['start time'] = f"{date} 10:00"
				data['end time'] = f"{date} 19:00"
				start_time, end_time = "10:00", "19:00"
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton('Подтвердить', callback_data='admin_confirm'),
			types.InlineKeyboardButton('Отменить', callback_data='cancel')
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Отменить бронированя {getDay(date)}\nС {start_time} по {end_time}", reply_markup=keyboard)

	elif cd.data.startswith('admin_confirm'):
		async with state.proxy() as data: 
			startTime = data['start time']
			endTime = data['end time']
		if stopReserv(startTime, endTime):
			await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Бронирования в это время остановленны")
		else: await bbot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text='Возникла ошибка при отмене бронирований')

	elif cd.data.startswith('admin_reserv'):
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton('Забронировать для себя', callback_data='admin_own_reserv'),
			types.InlineKeyboardButton('Забронировать для пользователя', callback_data='admin_user_reserv')
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Для кого вы хотите сделать бронирование",  reply_markup=keyboard)
	
	elif cd.data.startswith('admin_own_reserv') or cd.data.startswith('admin_back_to_dates'): 
		if cd.data.startswith('admin_own_reserv'):
			async with state.proxy() as data: data['user'] = cd.from_user.id
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in getDays():
			keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"admin_date_reserv={item['dayStamp']}"))
		keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Выберите день для бронирования:", reply_markup=keyboard)
	
	elif cd.data.startswith('admin_date_reserv'):
		date = cd.data.split('=')[1]
		async with state.proxy() as data: data['date'] = date
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in HOURS: 
			count = TABLE_COUNTS - checkDate(f"{date} {item.split('-')[0]}:00")
			if count > 0: callback = f"admin_set_time={item.split()[0]}={count}"
			else: callback = "pass"
			keyboard.add(types.InlineKeyboardButton(text=item.replace('count', str(count)), callback_data=callback))
		keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data="admin_back_to_dates"))
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выбранный день: {getDay(date)}\nВыберите с какого вренени отенить бронирования:", reply_markup=keyboard)

	elif cd.data.startswith('admin_set_time'):
		text, time, count = cd.data.split('=')
		count = int(count)
		async with state.proxy() as data: data['time'] = time
		maxRange = 11 if count >= 11 else count
		names = ['место', "места", "мест"]
		keys = []
		for i in range(1, maxRange):
			name = names[0] if i == 1 else names[1] if i > 1 and i < 5 else names[2]
			keys.append(types.InlineKeyboardButton(text=f"{i} {name}", callback_data=f'admin_table_count={i}'))
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*keys)
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Сколько мест вам нужно?\nМест сободно: {count}", reply_markup=keyboard)

	elif cd.data.startswith('admin_table_count'):
		count = cd.data.split('=')[1]
		async with state.proxy() as data: 
			data['count'] = count
			time = data['time']
			date = getDay(data['date'])
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton(text='Подтвердить', callback_data='admin_create_reserv'),
			types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
		])
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Выбранные данные:\nДата: {date}\nВремя: {time}\nКол-во мест: {count}", reply_markup=keyboard)

	elif cd.data.startswith('admin_create_reserv'):
		async with state.proxy() as data: 
			print(data)
			user = data['user']
			count = data['count']
			time = data['time']
			date = data['date']
		reversId = addReserv(user, f"{date} {time.split('-')[0]}:00", count)
		if reversId >= 0:
			await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Бронь успешно создана!\n{getDay(date)} {time}\nВаше рабочее место в Зеленом театре ждет вас", reply_markup=getReservKB(reversId))
		elif reversId == -1: await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Возникла ошибка при бронировании")
		elif reversId == -2: await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="В это время создание бронирования заблокирования")

	elif cd.data.startswith('admin_user_reserv'):
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text="Введите нико пользователя, на которого вы хотите сделат бронирование:")
		await Admin.setUser.set()
	
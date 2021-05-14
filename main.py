from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from bot import bot, dp
from ast import literal_eval
from sqlRequests import *
from state_machine import Registration
from local import local
from string_format import replaceAll
from dates import getDays, HOURS, getDay

@dp.message_handler(commands=['start'], state='*')
async def Start(message: types.Message) -> None:
	if checkUser(message.from_user.id): pass
	else: 
		await message.answer(local['hello'], reply_markup=types.ReplyKeyboardRemove(True))
		await Registration.firstName.set()

@dp.message_handler(state=Registration.firstName, )
async def setFName(message: types.Message, state: FSMContext) -> None:
	answ = message.text
	async with state.proxy() as data:
		data['firstName'] = answ
	await message.answer(local['input_lastName'])
	await Registration.lastName.set()
	
@dp.message_handler(state=Registration.lastName)
async def setLName(message: types.Message, state: FSMContext) -> None:
	answ = message.text
	async with state.proxy() as data:
		data['lastName'] = answ
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text="Send contact", request_contact=True))
	await message.answer(local['input_phone'], reply_markup=keyboard)
	await Registration.phone.set()

@dp.message_handler(content_types='contact', is_sender_contact=True, state=Registration.phone)
async def setContact(message: types.Message, state: FSMContext) -> None:
	user = message
	async with state.proxy() as data:
		data['phone'] = user['contact']['phone_number']
	await message.answer(local['input_command'], reply_markup=types.ReplyKeyboardRemove(True))
	await Registration.command.set()

@dp.message_handler(state=Registration.command)
async def setCommand(message: types.Message, state: FSMContext) -> None:
	answer = message.text
	async with state.proxy() as data:
		firstName = data['firstName']
		lastName = data['lastName']
		phone = data['phone']
		data['command'] = answer
	keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text="Подтвердить", callback_data='confirm_new_user'))
	await message.answer(
		replaceAll(local['confirm_user_data'], ['firstName', 'lastName', 'phone', 'command'], [firstName, lastName, phone, answer]),
		reply_markup=keyboard
		)

@dp.message_handler(commands=['reserv'])
async def getDate(message: types.Message):
	keyboard = types.InlineKeyboardMarkup(row_width=1)
	dates = getDays()
	for item in dates:
		keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"check_date={item['dayStamp']}"))
	keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
	await message.answer("Выберите день:", reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data, state=Registration)
async def FilterQueryHandler(cd: types.CallbackQuery, state: FSMContext):  
	if cd.data.startswith('confirm_new_user'):
		async with state.proxy() as data: 
			firstName = data['firstName']
			lastName = data['lastName']
			phone = data['phone']
			command = data['command']
		try: 
			addUser(cd.from_user.id, cd.from_user.username, firstName, lastName, phone, command)
			await bot.send_message(cd.from_user.id, local['success_reg'])
		except Exception as e: await bot.send_message(cd.from_user.id, text=local['smth_wrong'])
		finally: await state.finish()


@dp.callback_query_handler(lambda c: c.data)
async def ReervHandler(cd: types.CallbackQuery, state: FSMContext):
	if cd.data.startswith('check_date'):
		date = cd.data.split('=')[1]
		async with state.proxy() as data: data['date'] = date
		day = getDay(date)
		#По дате выборка из бд
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		for item in HOURS: keyboard.add(types.InlineKeyboardButton(text=item.replace('count', '35'), callback_data=f"set_time={item.split()[0]}"))
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
		time = cd.data.split('=')[1]
		async with state.proxy() as data: data['time'] = time
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton(text='1 место', callback_data='table_count=1'),
			types.InlineKeyboardButton(text='2 местa', callback_data='table_count=2'),
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
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Бронь успешно создана!\n{getDay(date)} {time}\nВаше рабочее место в Зеленом театре ждет вас")

def getReservKB(reservId):
	keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
		types.InlineKeyboardButton(text="Отменить бронь", callback_data=f'reserv_cancel={reservId}'),
		types.InlineKeyboardButton(text="Перенести бронь", callback_data=f'transfer_cancel={reservId}')
	])
	return keyboard

def getProfileKB():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, selective=True).add(*[
		types.KeyboardButton(text="Забронировать"),
		types.KeyboardButton(text="Посмотреть мои бронировки"),
		types.KeyboardButton(text="Связаться с администратором")
	])
	return keyboard

executor.start_polling(dp, skip_updates=True)
from aiogram.dispatcher import FSMContext
from aiogram import types
from bot import bot, dp
from keyboards import getReservKB
from dates import getDays, START_HOUR, END_HOUR, getDay
from sqlRequests import stopReserv
from state_machine import Admin
from config import PASSWORD


@dp.message_handler(commands=['login'])
async def adminLogin(message: types.Message): 
	await message.answer("Введите пароль для подтверждения личности:")
	await Admin.password.set()

@dp.message_handler(state=Admin.password)
async def adminPass(message: types.Message, state: FSMContext):
	answer = message.text
	if answer == PASSWORD:
		keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
			types.InlineKeyboardButton('Отменить бронирования определенного дня', callback_data="admin_cancel_reserv"),
			types.InlineKeyboardButton('Забронировать более 2-х мест', callback_data='admin_reserv'),
			types.InlineKeyboardButton('Выход', callback_data='admin_exit')
		])
		await message.answer('Вы открыли панель администратора', reply_markup=keyboard)
	else: await message.answer('Пароль не верный, свяжитесь с администратором для уточнения пароля')
	await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('admin'))
async def adminCallbacks(cd: types.CallbackQuery, state: FSMContext):
	if cd.data.startswith('admin_cancel_reserv'):
		keyboard = types.InlineKeyboardMarkup(row_width=1)
		dates = getDays()
		for item in dates:
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
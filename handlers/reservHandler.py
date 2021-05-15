from aiogram.dispatcher import FSMContext
from aiogram import types
from bot import bot, dp
from keyboards import getReservKB
from dates import getDays, getDay, HOURS

async def ReservHandler(cd: types.CallbackQuery, state: FSMContext):
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
		reversId = 1
		await bot.edit_message_text(chat_id=cd.from_user.id,message_id=cd.message.message_id, text=f"Бронь успешно создана!\n{getDay(date)} {time}\nВаше рабочее место в Зеленом театре ждет вас", reply_markup=getReservKB(reversId))

dp.register_callback_query_handler(ReservHandler, lambda c: c.data, state='*')
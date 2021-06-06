from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from bot import dp, bot
from sqlRequests import *
from state_machine import Registration
from local import local
from handlers.reservHandler import getReservKB
import handlers.registerHandler
import handlers.adminHandler
from config import ACTIVE, ADMINS_LIST
from dates import getDays, getDay
import notify


@dp.message_handler(commands=['reserv'])
async def startReserv(message: types.Message):
	keyboard = types.InlineKeyboardMarkup(row_width=1)
	dates = getDays()
	for item in dates:
		keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"check_date={item['dayStamp']}=reserv"))
	keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
	await message.answer("Выберите день:", reply_markup=keyboard)

@dp.message_handler(lambda c: c.text in ['Забронировать', 'Посмотреть мои бронировки', 'Связаться с администратором'], state='*')
async def Menu(message: types.Message, state: FSMContext) -> None:
	await state.finish()
	if message.text == 'Забронировать': await startReserv(message)
	elif message.text == 'Посмотреть мои бронировки': await getReserv(message)
	else: 
		for person in ADMINS_LIST:
			link = f"tg://user?id={person['user_id']}"
			keyboard = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Написать', url=link, ))
			try:
				await message.answer_contact(person['phone_number'], person['first_name'], reply_markup=keyboard)
			except Exception as e: await message.answer(f'''{person['first_name']}\n{person['phone_number']}''', reply_markup=keyboard, parse_mode='html')
			
async def getReserv(message: types.Message) -> None:
	reservs = getUserReserv(message.from_user.id)
	if len(reservs) == 0: 
		await message.answer('У вас еще нет бронирований, можете нажать кнопку "Забронировать" чтоб создать бронь')
		return
	for item in reservs:
		time = str(item[3]).split()[1][:5]
		endTime = str(item[4]).split()[1][:5]
		status = 'активна' if item[-2] == ACTIVE else 'остановлена'
		text = f"Бронь на {getDay(str(item[3]).split()[0])}\nВремя: {time}-{endTime}\nКол-во столов: {item[-3]}\nСтатус: {status}"
		await message.answer(text, reply_markup=getReservKB(item[0]))

executor.start_polling(dp, skip_updates=True)
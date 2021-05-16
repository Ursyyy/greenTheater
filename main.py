from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from bot import dp, bot
from sqlRequests import *
from state_machine import Registration
from local import local
from handlers.reservHandler import getReservKB
from keyboards import getProfileKB
import handlers.registerHandler
from dates import getDays, getDay#, getCurDay

@dp.message_handler(commands=['reserv'])
async def startReserv(message: types.Message):
	keyboard = types.InlineKeyboardMarkup(row_width=1)
	dates = getDays()
	for item in dates:
		keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"check_date={item['dayStamp']}"))
	keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
	await message.answer("Выберите день:", reply_markup=keyboard)


@dp.message_handler(lambda c: c.text in ['Забронировать', 'Посмотреть мои бронировки', 'Связаться с администратором'], state='*')
async def Menu(message: types.Message, state: FSMContext) -> None:
	await state.finish()
	if message.text == 'Забронировать': await startReserv(message)
	elif message.text == 'Посмотреть мои бронировки': await getReserv(message)
	else: pass

async def getReserv(message: types.Message) -> None:
	reservs = getUserReserv(message.from_user.id)
	if len(reservs) == 0: 
		await message.answer('У вас еще нет бронирований, можете нажать кнопку "Забронировать" чтоб создать бронь')
		return
	# [(1, '130923154', datetime.datetime(2021, 5, 16, 14, 7, 2), datetime.datetime(2021, 5, 20, 15, 0), 1, None)]
	for item in reservs:
		time = str(item[3]).split()[1][:5]
		endTime = int(time[:2]) + 1
		text = f"Бронь на {getDay(str(item[3]).split()[0])}\nВремя: {time}-{endTime}:00\nКол-во столов: {item[-2]}"
		await message.answer(text, reply_markup=getReservKB(item[0]))

executor.start_polling(dp, skip_updates=True)
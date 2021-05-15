from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from bot import dp, bot
from sqlRequests import *
from state_machine import Registration
from local import local
from handlers.reservHandler import getReservKB
from keyboards import getProfileKB
import handlers.registerHandler
from dates import getDays#, getCurDay



@dp.message_handler(commands=['reserv'])
async def getDate(message: types.Message):
	keyboard = types.InlineKeyboardMarkup(row_width=1)
	dates = getDays()
	for item in dates:
		keyboard.add(types.InlineKeyboardButton(text=item['dayName'], callback_data=f"check_date={item['dayStamp']}"))
	keyboard.add(types.InlineKeyboardButton(text="Отменить", callback_data="cancel"))
	await message.answer("Выберите день:", reply_markup=keyboard)


@dp.message_handler(lambda c: c.text in ['Забронировать', 'Посмотреть мои бронировки', 'Связаться с администратором'], state='*')
async def Menu(message: types.Message, state: FSMContext):
	await state.finish()
	if message.text == 'Забронировать': pass

@dp.callback_query_handler(lambda c: c.data, state=Registration)
async def registerUser(cd: types.CallbackQuery, state: FSMContext):  
	print('--')
	if cd.data.startswith('confirm_new_user'):
		async with state.proxy() as data: 
			firstName = data['firstName']
			lastName = data['lastName']
			phone = data['phone']
			command = data['command']
		try: 
			addUser(cd.from_user.id, cd.from_user.username, firstName, lastName, phone, command)
			await bot.send_message(cd.from_user.id, local['success_reg'], reply_markup=getProfileKB())
		except Exception as e: await bot.send_message(cd.from_user.id, text=local['smth_wrong'])
		finally: await state.finish()


executor.start_polling(dp, skip_updates=True)
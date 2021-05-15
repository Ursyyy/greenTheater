from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram import types
from bot import dp, bot
from local import local
from state_machine import Registration
from keyboards import getProfileKB
from sqlRequests import addUser, checkUser
from string_format import replaceAll

@dp.message_handler(commands=['start', 'register', 'reg'], state='*')
async def Start(message: types.Message) -> None:
	if checkUser(message.from_user.id): await message.answer("Вы уже авторизовались и по кнопке \"Забронировать\" можете сделать бронь", reply_markup=getProfileKB())
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

@dp.callback_query_handler(lambda c: c.data, state=Registration)
async def FilterQueryHandler(cd: types.CallbackQuery, state: FSMContext):  
	if cd.data.startswith('confirm_new_user'):
		async with state.proxy() as data: 
			firstName = data['firstName']
			lastName = data['lastName']
			phone = data['phone']
			command = data['command']
		try: 
			await bot.delete_message(cd.from_user.id, cd.message.message_id)
			addUser(cd.from_user.id, cd.from_user.username, firstName, lastName, phone, command)
			await bot.send_message(cd.from_user.id, local['success_reg'], reply_markup=getProfileKB())
		except Exception as e: await bot.send_message(cd.from_user.id, text=local['smth_wrong'])
		finally: await state.finish()

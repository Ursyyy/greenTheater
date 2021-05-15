from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram import types
from bot import dp
from local import local
from state_machine import Registration
from keyboards import getProfileKB
from sqlRequests import addUser
from string_format import replaceAll

async def setFName(message: types.Message, state: FSMContext) -> None:
	answ = message.text
	async with state.proxy() as data:
		data['firstName'] = answ
	await message.answer(local['input_lastName'])
	await Registration.lastName.set()
	
async def setLName(message: types.Message, state: FSMContext) -> None:
	answ = message.text
	async with state.proxy() as data:
		data['lastName'] = answ
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True).add(types.KeyboardButton(text="Send contact", request_contact=True))
	await message.answer(local['input_phone'], reply_markup=keyboard)
	await Registration.phone.set()

async def setContact(message: types.Message, state: FSMContext) -> None:
	user = message
	async with state.proxy() as data:
		data['phone'] = user['contact']['phone_number']
	await message.answer(local['input_command'], reply_markup=types.ReplyKeyboardRemove(True))
	await Registration.command.set()

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


dp.register_message_handler(setFName, state=Registration.firstName)
dp.register_message_handler(setLName, state=Registration.lastName)
dp.register_message_handler(setCommand, state=Registration.command)
dp.register_message_handler(setContact, content_types='contact', state=Registration.phone)
# dp.register_callback_query_handler(registerUser, lambda c: c.data, state='*')
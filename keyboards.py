from aiogram import types

def getProfileKB():
	keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, selective=True, row_width=2).add(*[
		types.KeyboardButton(text="Забронировать"),
		types.KeyboardButton(text="Посмотреть мои бронировки"),
		types.KeyboardButton(text="Связаться с администратором")
	])
	return keyboard

def getReservKB(reservId):
	keyboard = types.InlineKeyboardMarkup(row_width=1).add(*[
		types.InlineKeyboardButton(text="Отменить бронь", callback_data=f'reserv_cancel={reservId}'),
		types.InlineKeyboardButton(text="Перенести бронь", callback_data=f'transfer_reserv={reservId}')
	])
	return keyboard
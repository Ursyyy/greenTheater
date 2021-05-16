from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.types import message
from bot import bot, dp
from keyboards import getReservKB
from dates import getDays, getDay, HOURS
from sqlRequests import addReserv, checkDate, removeReserv, changeTime
from config import TABLE_COUNTS


@dp.message_handler(commands=['login'])
async def adminLogin(message: types.Message): 
    await message.answer("Введите пароль для подтверждения личности:")
    
from aiogram.dispatcher.filters import state
from aiogram.dispatcher.filters.state import State, StatesGroup

class Registration(StatesGroup):
    firstName = State()
    lastName = State()
    phone = State()
    command = State()

class Admin(StatesGroup): 
    password = State()
    setUser = State()
    notifyText = State()
    description = State()
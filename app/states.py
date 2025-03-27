from aiogram.fsm.state import State, StatesGroup

class Chat(StatesGroup):
    busy = State()
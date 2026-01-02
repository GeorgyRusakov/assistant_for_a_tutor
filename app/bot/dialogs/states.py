from aiogram.fsm.state import State, StatesGroup


class StartWork(StatesGroup):
    menu = State()


class StartSG(StatesGroup):
    start = State()
    helper = State()


class AddDeleteStud(StatesGroup):
    select_opt = State()
    input_name = State()
    select_grade = State()
    input_price = State()
    select_subject = State()
    delete = State()



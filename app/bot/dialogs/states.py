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


class ClassJournal(StatesGroup):
    preview = State()
    journal = State()
    selected_stud = State()


class Timetable(StatesGroup):
    preview = State()
    view_timetable = State()
    add_timetable_step_1 = State()
    add_timetable_step_2 = State()
    add_timetable_step_3 = State()
    add_timetable_step_4 = State()

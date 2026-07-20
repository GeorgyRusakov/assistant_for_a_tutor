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
    journal_year = State()
    journal_month = State()
    journal_view = State()
    card_view = State()
    add_lesson = State()
    selected_stud = State()


class Timetable(StatesGroup):
    preview = State()
    view_timetable = State()
    add_timetable_step_1 = State()
    add_timetable_step_2 = State()
    add_timetable_step_3 = State()
    add_timetable_step_4 = State()


class Finance(StatesGroup):
    finpreview = State()
    fin_report = State()
    fin_report_week = State()
    fin_report_month = State()

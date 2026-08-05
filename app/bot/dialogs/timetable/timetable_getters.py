from babel.dates import get_day_names
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ManagedRadio
import logging
from app.bot.dialogs import states
from pprint import pprint
from app.infrastructure.database.db import get_students, add_timetable, get_timetable, get_context_last_id_stud, \
    get_subject_stud
from psycopg import AsyncConnection
from aiogram_dialog.widgets.text import Jinja


logger = logging.getLogger(__name__)

async def timetable_preview_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    # Сразу добавляем словарь дней недели в dialog_data
    if dialog_manager.dialog_data.get('ru_day_dict') is None:
        await lst_subject_add_data(dialog_manager)

    return {'window_preview_timetable': local['window_preview_timetable']}


async def lst_subject_add_data(
        dialog_manager: DialogManager):  # Функция добавления сокращенных дней недели в dialog_data
    ru_day_wide = get_day_names('wide', locale='ru_RU')
    ru_day_dict_wide = dict(ru_day_wide)
    dialog_manager.dialog_data.update(ru_day_dict=ru_day_dict_wide)


async def timetable_view_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    current_page = await dialog_manager.find('id_stub_scroll').get_page()
    conn: AsyncConnection = dialog_manager.middleware_data.get('conn')
    ru_day_dict = dialog_manager.dialog_data.get('ru_day_dict')
    day_week: str = ru_day_dict.get(current_page)
    timetable = await get_timetable(conn=conn, day_week=day_week)

    if timetable:
        table_text = "```\n\n"
        table_text += "═" * 25 + "\n\n"
        for idx, lesson in enumerate(timetable, 1):
            name = lesson[0]  # Имя ученика
            subject = lesson[1]  # Предмет
            time = lesson[3]  # Время

            table_text += f"{idx}. 👤 {name}\n"
            table_text += f"   📚 {subject}\n"
            table_text += f"   🕐 {time}\n\n"

        table_text += "═" * 25
        table_text += "```"
    else:
        table_text = "📅 В этот день занятий нет"

    return {
        'ru_day': day_week.capitalize(),
        'timetable_text': table_text
    }

async def get_stud_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    stud_row = await get_students(conn)
    # print(stud_row)
    # print(dialog_manager.start_data)
    lst_stud = [(f'{i[1]}', i[0]) for i in stud_row]
    dialog_manager.dialog_data.update(lst_stud=lst_stud)
    return {'stud_row': lst_stud,
            'len_stud_row': len(stud_row),
            'window_add_lesson_view': local['window_add_lesson_view']}

async def timetable_add_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    subjects = []
    conn: AsyncConnection = dialog_manager.middleware_data.get('conn')

    if dialog_manager.dialog_data.get('current_id_stud') is not None:

        current_id_stud = dialog_manager.dialog_data.get('current_id_stud')
        subjects = await get_subject_stud(conn, current_id_stud)
        print(subjects)
    else:
        logger.info('id ученика не найден, список предметов не получен')

    if not subjects:
        subjects = [
            (1, 'Математика'),
            (2, 'Физика'),
        ]

    ru_day_abbreviated = get_day_names('abbreviated', locale='ru_Ru')

    ru_day_dict_abbrev = dict(ru_day_abbreviated)

    if dialog_manager.dialog_data.get('lst_subject') is None:
        dialog_manager.dialog_data.update(lst_subject=subjects)

    return {"subjects": subjects,
            "ru_day": ru_day_dict_abbrev.items()}


async def input_time_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'input_time_text': local['input_time_text']}

async def finish_timetable_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    radio1_subject = dialog_manager.find(
        'ch_subject').get_checked()  # Получаем данные с нажатой кнопки по предмету

    radio2_day_week = dialog_manager.find('radio2_day_week').get_checked()  # Нажатая кнопка дня недели

    radio3_stud = dialog_manager.find('radio3_stud').get_checked()  # Нажатая кнопка по ученику

    # time_input = dialog_manager.find('price_input').get_value()  # Получаем введенное время занятия
    time_hour = dialog_manager.dialog_data.get('time_hour')
    time_minute = dialog_manager.dialog_data.get('time_minute')
    input_time = f'{time_hour}:{time_minute}'

    lst_stud = []  # Если начинаем добавлять расписание из окна добавления
    # ученика, то список студентов не загружается в dialog_data
    if dialog_manager.dialog_data.get('lst_stud') is None:
        conn = dialog_manager.middleware_data.get('conn')
        stud_row = await get_students(conn)
        lst_stud = [(f'{i[1]}', i[0]) for i in stud_row]
    else:
        lst_stud = dialog_manager.dialog_data.get('lst_stud')

    if dialog_manager.dialog_data.get('ru_day_dict') is None:
        await lst_subject_add_data(dialog_manager)

    lst_subject = dialog_manager.dialog_data.get('lst_subject')
    print(lst_subject)
    ru_day_dict = dialog_manager.dialog_data.get('ru_day_dict')

    name_stud = [lst_stud[i][0] for i in range(len(lst_stud)) if lst_stud[i][1] == int(radio3_stud)]
    subject = [lst_subject[i][1] for i in range(len(lst_subject)) if lst_subject[i][0] == int(radio1_subject)]
    day_week = ru_day_dict.get(int(radio2_day_week))

    dialog_manager.dialog_data.update(contex_timetable=[radio3_stud, radio1_subject, day_week, input_time])

    finish_text = f'Предмет: {subject[0]} \n' \
                  f'День недели: {day_week} \n' \
                  f'Время: {input_time} \n' \
                  f'Ученик: {name_stud[0]} \n'

    return {'finish_text': finish_text}


async def set_stud_default(_, dialog_manager: DialogManager):
    context_stud: list = []

    if dialog_manager.start_data is not None:
        context_stud = dialog_manager.start_data

        conn: AsyncConnection = dialog_manager.middleware_data.get('conn')
        id_stud = await get_context_last_id_stud(conn, *context_stud)

        print(dialog_manager.start_data)

        if id_stud is not None:
            dialog_manager.dialog_data.update(current_id_stud=id_stud[0])
            radio_stud: ManagedRadio = dialog_manager.find('radio3_stud')
            await radio_stud.set_checked(str(id_stud[0]))

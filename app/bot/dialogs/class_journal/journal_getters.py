from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager, StartMode, Window, ShowMode, ChatEvent
# from aiogram.enums import ButtonStyle
import logging
from app.infrastructure.database.db import get_students, get_subject_stud, get_id_subject_stud, add_class_journal
from psycopg import AsyncConnection
from babel.dates import format_date
import calendar
from datetime import datetime

logger = logging.getLogger(__name__)

async def journal_preview_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'window_preview_hello': local['window_preview_hello']}

async def get_stud_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    stud_row = await get_students(conn)
    # print(stud_row)
    lst_stud = [(f'{i[1]}', i[0]) for i in stud_row]
    # pprint(lst_stud)
    dialog_manager.dialog_data.update(stud_row=lst_stud)
    return {'stud_row': lst_stud,
            'len_stud_row': len(stud_row),
            'window_add_lesson_view': local['window_add_lesson_view']}


async def product_getter(**_kwargs):
    months_ru = [calendar.month_name[i] for i in range(1, 13)]
    return {
        "products": [(f"Product {i}", i) for i in range(1, 30)],
        "months_ru": months_ru,
    }


async def selected_student_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    selected_id_stud = dialog_manager.dialog_data.get('selected_stud')

    lst_stud: tuple = dialog_manager.dialog_data.get('stud_row')

    selected_stud = [lst_stud[i][0] for i in range(len(lst_stud)) if lst_stud[i][1] == selected_id_stud]
    subjects = await get_subject_stud(conn, int(selected_id_stud))

    if dialog_manager.dialog_data.get('date') is None:
        current_date = datetime.now()
        formatted_date = format_date(current_date, format='d MMMM', locale='ru')
        dialog_manager.dialog_data.update(date=current_date)
    else:
        current_date = dialog_manager.dialog_data.get('date')
        print(current_date)
        formatted_date = format_date(current_date, format='d MMMM', locale='ru_RU')

    return {'selected_stud': selected_stud[0],
            'subjects': subjects,
            'current_date': formatted_date}
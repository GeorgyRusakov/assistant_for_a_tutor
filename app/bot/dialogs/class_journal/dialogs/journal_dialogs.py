from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode, ChatEvent
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start, Next, Back, Cancel, SwitchTo, Select, \
    Multiselect, ManagedMultiselect, ManagedCounter, Counter, Checkbox, Radio, ScrollingGroup, ListGroup, TimeSelect, \
    Calendar, ManagedCalendar
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
import logging
from app.bot.dialogs import states
from pprint import pprint
from app.infrastructure.database.db import get_students, get_subject_stud, get_id_subject_stud, add_class_journal
from psycopg import AsyncConnection
from operator import itemgetter
from app.bot.dialogs.common import MAIN_MENU_BUTTON
from typing import Any
from aiogram_dialog.widgets.style import Style
from datetime import date, datetime, timedelta
from babel.dates import format_date

logger = logging.getLogger(__name__)


async def get_stud_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    stud_row = await get_students(conn)
    # print(stud_row)
    lst_stud = [(f'{i[1]}', i[0]) for i in stud_row]
    # pprint(lst_stud)
    dialog_manager.dialog_data.update(stud_row=lst_stud)
    return {'stud_row': lst_stud,
            'len_stud_row': len(stud_row),
            'window_journal_view': local['window_journal_view']}


async def on_click(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=states.StartWork.menu)


async def on_text_click(
        event: CallbackQuery,
        widget: ManagedCounter,
        dialog_manager: DialogManager
) -> None:
    print(widget.widget.text)
    print(event.answer(f"Value: {widget.get_value()}"))
    await event.answer(f"Value: {widget.get_value()}")


async def journal_preview_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'window_preview_hello': local['window_preview_hello']}


async def on_student_click(callback: CallbackQuery, widget: Any, manager: DialogManager, selected_item: str):
    manager.dialog_data.update(selected_stud=int(selected_item))
    await manager.next()


async def on_date_clicked(callback: ChatEvent, widget: ManagedCalendar, dialog_manager: DialogManager,
                          selected_date: date, /, ):
    await callback.answer(str(selected_date))


async def date_button_prev_clicked(callback: CallbackQuery, button: Button,
                                   dialog_manager: DialogManager):
    current_day: date = dialog_manager.dialog_data.get('date')
    print(current_day)
    next_day = current_day - timedelta(days=1)
    dialog_manager.dialog_data.update(date=next_day)


async def date_button_next_clicked(callback: CallbackQuery, button: Button,
                                   dialog_manager: DialogManager):
    current_day: date = dialog_manager.dialog_data.get('date')
    print(current_day)
    next_day = current_day + timedelta(days=1)
    dialog_manager.dialog_data.update(date=next_day)


async def add_new_lesson(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    widget = dialog_manager.find('checked_lesson')
    if widget.is_checked():
        logger.info('Записываем новое занятие в бд')
        conn = dialog_manager.middleware_data.get('conn')
        sub_select = dialog_manager.find('radio1_subject').get_checked()
        # print(type(sub_select))
        id_student = dialog_manager.dialog_data.get('selected_stud')
        select_day = dialog_manager.dialog_data.get('date')
        print(select_day)
        id_subject_student = await get_id_subject_stud(conn, id_student, int(sub_select))
        print(id_subject_student)
        await add_class_journal(conn, id_subject_student[0], select_day)
        await dialog_manager.switch_to(state=states.ClassJournal.journal)


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


preview_journal = Window(
    Format('{window_preview_hello}'),
    Column(
        Next(Const('Просмотреть журнал')),
        MAIN_MENU_BUTTON,
    ),
    getter=journal_preview_getter,
    state=states.ClassJournal.preview
)

view_journal = Window(
    Format('{window_journal_view}'),
    ScrollingGroup(
        Select(
            Format("{item[0]}"),
            id='select_student',
            item_id_getter=itemgetter(1),
            items='stud_row',
            on_click=on_student_click,
        ),
        width=1,
        height=5,
        id="scroll_with_pager",
    ),
    MAIN_MENU_BUTTON,
    state=states.ClassJournal.journal,
    getter=get_stud_getter,
)

selected_student = Window(
    Format("Вы выбрали ученика: {selected_stud}"),
    Const("Добавляем занятие: "),
    Radio(
        checked_text=Format('[✅] {item[1]}'),
        unchecked_text=Format('[ ] {item[1]}'),
        id='radio1_subject',
        item_id_getter=lambda x: x[0],
        items='subjects',
        # on_click=radio1_click,
    ),
    Checkbox(
        unchecked_text=Const('[ ] Новое занятие'),
        checked_text=Const('[✅] Новое занятие'),
        id='checked_lesson',
        checked_style=Style("success"),
        default=True,
    ),
    Row(
        Button(text=Const('<'),
               id='date_button_prev',
               on_click=date_button_prev_clicked),
        Button(
            text=Format('{current_date}'),
            id='date_button',
        ),
        Button(text=Const('>'),
               id='date_button_next',
               on_click=date_button_next_clicked),

    ),
    # Calendar(
    #     id='calender',
    #     on_click=on_date_clicked,
    # ),
    Button(
        Const('Подтвержаем занятие'), id='button_new_lesson', on_click=add_new_lesson
    ),
    Back(Const('⬅️Назад')),
    MAIN_MENU_BUTTON,
    getter=selected_student_getter,
    state=states.ClassJournal.selected_stud,
)

journal_dialogs = Dialog(
    preview_journal,
    view_journal,
    selected_student
)

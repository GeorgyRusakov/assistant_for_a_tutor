from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, StartMode, ShowMode, ChatEvent
from aiogram_dialog.widgets.kbd import Button
# from aiogram.enums import ButtonStyle
import logging
from app.bot.dialogs import states
from pprint import pprint
from app.infrastructure.database.db import get_id_subject_stud, add_class_journal
from typing import Any
from datetime import date, timedelta


logger = logging.getLogger(__name__)


async def on_student_click(callback: CallbackQuery, widget: Any, manager: DialogManager, selected_item: str):
    manager.dialog_data.update(selected_stud=int(selected_item))
    await manager.switch_to(state=states.ClassJournal.selected_stud)


async def on_year_click(callback: CallbackQuery, widget: Any, manager: DialogManager, selected_item: str):
    manager.dialog_data.update(selected_year=int(selected_item))
    logger.info(f'Выбранный год: {selected_item}')
    await manager.switch_to(state=states.ClassJournal.journal_month)


async def on_month_click(callback: CallbackQuery, widget: Any, manager: DialogManager, selected_item: str):
    manager.dialog_data.update(selected_month=int(selected_item))
    logger.info(f'Выбранный месяц: {selected_item}')
    await manager.switch_to(state=states.ClassJournal.journal_view)

async def on_class_card_click(callback: CallbackQuery, widget: Any, manager: DialogManager, selected_item: str):
    manager.dialog_data.update(selected_id_class_card=int(selected_item))
    logger.info(f'ID выбранного занятия: {selected_item}')
    await manager.switch_to(state=states.ClassJournal.card_view)

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
        await dialog_manager.switch_to(state=states.ClassJournal.add_lesson)
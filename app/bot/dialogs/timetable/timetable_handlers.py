from aiogram.types import CallbackQuery, User
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button
import logging
from app.bot.dialogs import states
from pprint import pprint
from app.infrastructure.database.db import add_timetable
from psycopg import AsyncConnection

logger = logging.getLogger(__name__)

async def hour_click(callback: CallbackQuery, counter, dialog_manager: DialogManager, value):
    dialog_manager.dialog_data.update(time_hour=value)
    print(value)


async def minute_click(callback: CallbackQuery, counter, dialog_manager: DialogManager, value):
    dialog_manager.dialog_data.update(time_minute=value)
    print(value)

async def sending_timetable_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    conn: AsyncConnection = dialog_manager.middleware_data.get('conn')
    context_timetable = dialog_manager.dialog_data.get('contex_timetable')
    logger.info('Записываем данные в бд')
    await add_timetable(conn, *context_timetable)

    await callback.message.answer(text='Данные отправлены на сервер! Возвращаемся в основное меню')
    await dialog_manager.start(state=states.StartWork.menu, show_mode=ShowMode.DELETE_AND_SEND)
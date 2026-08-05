from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ChatEvent
from aiogram_dialog.widgets.kbd import Button
# from aiogram.enums import ButtonStyle
import logging
from app.bot.dialogs import states
from pprint import pprint
from typing import Any
from datetime import date, timedelta

logger = logging.getLogger(__name__)

async def on_year_click(callback: CallbackQuery, widget: Any, manager: DialogManager, selected_item: str):
    manager.dialog_data.update(selected_year=int(selected_item))
    logger.info(f'Выбранный год: {selected_item}')
    await manager.switch_to(state=states.Finance.select_fin_report_by_month)


async def on_month_click(callback: CallbackQuery, widget: Any, manager: DialogManager, selected_item: str):
    manager.dialog_data.update(selected_month=int(selected_item))
    logger.info(f'Выбранный месяц: {selected_item}')
    await manager.switch_to(state=states.Finance.selected_fin_report_by_month_year)


async def on_year_click_general_report(callback: CallbackQuery, widget: Any, manager: DialogManager, selected_item: str):
    manager.dialog_data.update(selected_year=int(selected_item))
    logger.info(f'Выбранный год: {selected_item}')
    await manager.switch_to(state=states.Finance.fin_all_time_report)
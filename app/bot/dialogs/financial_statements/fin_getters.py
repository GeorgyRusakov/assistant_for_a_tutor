from aiogram.enums import ParseMode
from aiogram_dialog import DialogManager
import logging
from app.bot.dialogs import states
from pprint import pprint
from app.infrastructure.database.db import get_students, get_subject_stud, get_id_subject_stud, add_class_journal, \
    get_sum_price_week, get_sum_price_month
from psycopg import AsyncConnection
from typing import Any
from ...services.financial_service import create_financial_service

from datetime import datetime, timedelta, date

logger = logging.getLogger(__name__)


async def finpreview_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'finpreview': local.get('finpreview')}


async def get_current_date_week(date: date) -> tuple[date, date]:
    # Понедельник: текущая дата - (день недели: 0-Пн, 6-Вс)
    start_week = date - timedelta(days=date.weekday())
    # Воскресенье: понедельник + 6 дней
    end_week = start_week + timedelta(days=6)
    logger.info(f"Начало недели (Пн): {start_week}")
    logger.info(f"Конец недели (Вс): {end_week}")
    # week_days = [start_week + timedelta(days=i) for i in range(7)]
    # print("Все дни:", week_days)
    return start_week, end_week


async def get_current_date_month(date: date) -> int:
    current_month = date.month
    logger.info(f"Номер текущего месяца: {current_month}")
    return current_month


async def fin_report_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    pass


async def fin_report_week_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    report_week: tuple = dialog_manager.dialog_data.get('week_report', ())

    if report_week:
        res_sum_week, res_report_table = report_week
        logger.info('Получаем данные без повторного обращения к базе')
    else:
        service = create_financial_service(dialog_manager)
        res_sum_week, res_report_table = await service.make_week_report()
        dialog_manager.dialog_data.update(week_report=(res_sum_week, res_report_table))

    # today = datetime.now().date()
    # start_end_week: tuple = await get_current_date_week(today)
    # conn: AsyncConnection = dialog_manager.middleware_data.get('conn')
    # sum_price_week = await get_sum_price_week(conn, *start_end_week)

    # current_month = await get_current_date_month(today)

    # sum_price_month = await get_sum_price_month(conn, current_month)

    return {'sum_total_week': res_sum_week,
            'report_table': res_report_table}


async def fin_report_month_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    pass
from aiogram.enums import ParseMode
from aiogram_dialog import DialogManager
import logging
from app.bot.dialogs import states
from pprint import pprint
from app.infrastructure.database.db import get_students, get_subject_stud, get_id_subject_stud, add_class_journal, \
    get_sum_price_week, get_sum_price_month, get_classes_by_year, get_classes_by_month
from psycopg import AsyncConnection
from typing import Any
from ...services.financial.financial_service import create_week_financial_service, create_month_financial_service
from ...services.financial.general_statistics import create_general_financial_report
from babel.dates import get_month_names
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
    week_report: tuple = dialog_manager.dialog_data.get('week_report', ())

    if week_report:
        res_sum_week, res_report_table = week_report
        logger.info('Получаем данные без повторного обращения к базе')
    else:
        service = create_week_financial_service(dialog_manager)
        res_sum_week, res_report_table = await service.make_week_report()
        dialog_manager.dialog_data.update(week_report=(res_sum_week, res_report_table))

    return {'sum_total_week': res_sum_week,
            'report_table': res_report_table}


async def fin_report_month_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    month_report: tuple = dialog_manager.dialog_data.get('month_report', ())

    if month_report:
        res_sum_month, res_report_table = month_report
        logger.info('Получаем данные без повторного обращения к базе')
    else:
        service = create_month_financial_service(dialog_manager)
        res_sum_month, res_report_table = await service.make_month_report()
        dialog_manager.dialog_data.update(month_report=(res_sum_month, res_report_table))

    return {'sum_total_month': res_sum_month,
            'report_table': res_report_table}


async def get_year_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    try:
        year_row = await get_classes_by_year(conn)

        if not year_row:
            logger.error("Не удалось получить список уникальных лет")
            raise RuntimeError("Ошибка получения списка уникальных лет")

        logger.info(f"Список лет: {year_row}")

        return {'year_row': year_row}

    except Exception as e:
        logger.exception('Ошибка при получении списка годов: %s', e)


async def get_month_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    selected_year = dialog_manager.dialog_data.get('selected_year')

    try:
        month_row = await get_classes_by_month(conn, selected_year)

        if not month_row:
            logger.error("Не удалось получить список месяцев")
            raise RuntimeError("Ошибка получения списка месяцев")

        logger.info(f'Список месяцев: {month_row}')

        months_names = get_month_names(
                "wide", context="stand-alone", locale='ru_RU',
            )

        months_list = [(*i, months_names[int(*i)].capitalize()) for i in month_row]

        logger.info(f'Список Номер - Месяц: {months_list}')

        return {'months_list': months_list}

    except Exception as e:
        logger.exception("Ошибка при получении списка месяцев: %s", e)



async def select_fin_report_by_month_year_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    selected_month = dialog_manager.dialog_data.get('selected_month')
    selected_year = dialog_manager.dialog_data.get('selected_year')

    service = create_month_financial_service(dialog_manager)
    res_sum_month, res_report_table = await service.make_select_month_report(selected_year, selected_month)

    months_names = get_month_names(
                "wide", context="stand-alone", locale='ru_RU',
            )

    return {'sum_total_month': res_sum_month,
            'report_table': res_report_table,
            'month_name': months_names[int(selected_month)]}


async def fin_general_report_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    selected_year = dialog_manager.dialog_data.get('selected_year')

    service = create_general_financial_report(dialog_manager)

    res_general_sum, general_report_table = await service.make_general_statistics(selected_year)

    return {"year": selected_year,
            "report_table": general_report_table,
            "general_sum": res_general_sum}

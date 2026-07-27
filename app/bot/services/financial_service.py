import logging
from typing import List, Tuple
from datetime import datetime, timedelta, date

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import ManagedRadio, ManagedListGroup, ManagedCheckbox, ManagedCounter

from ..constants.widget_ids import WIDGETS
from ...infrastructure.database.models.student import StudentData
from ...infrastructure.database.db import get_sum_price_week, get_statistics_for_the_week, get_sum_price_month
from ..constants.widget_ids import WIDGETS
from psycopg import AsyncConnection
from ...infrastructure.database.models.financial import FinancialData


logger = logging.getLogger(__name__)

class FinancialService:
    """
    Сервис для составления финансовой отчетности
    """

    def __init__(self, dialog_manager: DialogManager):
        self.dm = dialog_manager

    async def make_week_report(self) -> tuple[int, str]:
        """Собирает итоговый результат для отчета за неделю"""
        start_end_week: tuple = self._get_current_dates_week()

        conn: AsyncConnection = self.dm.middleware_data.get(WIDGETS.DIALOG_CONNECTION)

        if not conn:
            raise RuntimeError("Соединение с БД не найдено")

        res_sum_week = await self._get_price_for_report_week(conn, *start_end_week)

        statistics = await self._get_statistics_for_the_week(conn, *start_end_week)

        res_report_table = self._generate_financial_table(statistics)

        logger.info('Получили отчет за неделю: %s, %s', res_sum_week, res_report_table)

        return (res_sum_week, res_report_table)

    def _get_current_date_month(self, date: date) -> int:
        current_month = date.month

        logger.info(f"Номер текущего месяца: {current_month}")

        return current_month

    def _get_current_dates_week(self) -> tuple[date, date]:
        """Получает начало и конец текущей недели"""
        today = datetime.now().date()

        start_week = today - timedelta(days=today.weekday())

        end_week = start_week + timedelta(days=6)

        logger.info('Начало: %s, и конец: %s недели', start_week, end_week)

        return (start_week, end_week)

    async def _get_price_for_report_week(self, conn, start_week, end_week) -> int:
        """Получает суммарную стоимость занятий за неделю для отчета"""
        try:
            res_week = await get_sum_price_week(conn, start_week, end_week)

            logger.info('Сумма занятий за неделю: %s', res_week)

            if not res_week[0]:
                return 0

            return res_week[0]

        except Exception as e:
            logger.exception("Ошибка получения суммы за неделю %s:", e)
            raise

    async def _get_statistics_for_the_week(self, conn, start_week, end_week) -> List[FinancialData]:
        """Получает статистику за неделю"""
        try:
            statistics = await get_statistics_for_the_week(conn, start_week, end_week)

            logger.info('Статистика за неделю: %s', statistics)

            if not statistics[0]:
                return []

            return [FinancialData(*statistic) for statistic in statistics]

        except Exception as e:
            logger.exception("Ошибка получения статистики за неделю %s:", e)
            raise

    def _generate_financial_table(self, statistics: List[FinancialData]) -> str:
        """Генерирует таблицу из полученной статистики"""
        if statistics:
            table_text = "```\n"

            table_text += "┌────────────────────┬─────────────────────┬──────────────┐\n"
            table_text += "│ Ученик             │ Количество занятий  │ Сумма, руб.  │\n"
            table_text += "├────────────────────┼─────────────────────┼──────────────┤\n"

            for statistic in statistics:
                name = statistic.name[:16].ljust(18)
                number = str(statistic.number).ljust(19)
                total = str(statistic.total).ljust(12)
                table_text += f"│ {name} │ {number} │ {total} │ \n"
                # table_text += "├────────────────────┼─────────────────────┼──────────────┤\n"

            table_text += "└────────────────────┴─────────────────────┴──────────────┘\n"
            table_text += "```"
        else:
            table_text = 'На этой неделе пока не было занятий'

        return table_text


def create_financial_service(dialog_manager: DialogManager) -> FinancialService:
    """Фабрика для создания сервиса."""
    return FinancialService(dialog_manager)
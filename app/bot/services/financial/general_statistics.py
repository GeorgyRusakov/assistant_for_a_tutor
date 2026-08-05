import logging
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker

from typing import List, Tuple
from datetime import datetime, timedelta, date

from aiogram_dialog import DialogManager
from ...constants.widget_ids import WIDGETS
from psycopg import AsyncConnection
from babel.dates import get_month_names
from ....infrastructure.database.models.financial import GeneralFinancialData
from ....infrastructure.database.db import get_general_statistics_for_the_year, get_general_sum_year

logger = logging.getLogger(__name__)

class GeneralFinancialReport:
    """Сервис для составления общей финансовой статистики"""
    def  __init__(self, dialog_manager: DialogManager):
        self.dm = dialog_manager

    async def make_general_statistics(self, year):
        conn: AsyncConnection = self.dm.middleware_data.get(WIDGETS.DIALOG_CONNECTION)

        if not conn:
            raise RuntimeError("Соединение с БД не найдено")

        statistics: list[GeneralFinancialData] = await self._get_general_statistics_for_the_year(conn, year)

        months_lst = self._get_months_list()

        months_dict = self._get_months_dict()

        total = await self._get_general_sum_year(conn, year)

        prepare_data = await self._prepare_data_for_table(statistics, months_dict)

        general_table = await self._generate_general_report_table(prepare_data)

        self._generate_graph(statistics, year, months_lst)

        return total, general_table


    def _generate_graph(self, statistics: List[GeneralFinancialData], year, months):
        total = [0] * 12

        for data in statistics:
            total[int(data.month) - 1] = data.total

        logger.info('Список доходов за каждый месяц в теч. года: %s', total)

        # Создаем фигуру и оси
        fig, ax = plt.subplots(figsize=(18, 10))

        # Устанавливаем темно-серый фон для всей фигуры
        fig.patch.set_facecolor('#181717')

        # Устанавливаем темно-серый фон для области построения
        ax.set_facecolor('#181717')

        # Делаем оси белыми
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_color('#181717')
        ax.spines['right'].set_color("#181717")

        # Делаем подписи на осях белыми
        ax.tick_params(colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')

        # Используем числовые позиции для столбцов
        months_pos = np.arange(0, 12)  # от 0 до 11

        # Добавляем столбцы оранжевого цвета (используем months_pos как позиции)
        ax.bar(months_pos, total, color="orange")

        # Устанавливаем подписи месяцев на соответствующие позиции
        ax.set_xticks(months_pos)
        ax.set_xticklabels(months, rotation=45)

        ax.yaxis.set_major_locator(ticker.MultipleLocator(2000))

        # Подписи осей и заголовок
        ax.set_title('Статистика, 2026 г.')

        ax.set_xlabel('Месяц', labelpad=10)

        ax.set_ylabel('Сумма, ₽', rotation=0, labelpad=10, ha='right', va='center')

        folder = 'C:/Users/rusak/OneDrive/Рабочий стол/PythonProject/TelegramBots/TutorHelper/assistant_for_a_tutor/graphs'
        os.makedirs(folder, exist_ok=True)
        plt.savefig(os.path.join(folder, f'Статистика, {year} г..png'), facecolor='#181717', bbox_inches='tight')

    async def _generate_general_report_table(self, data: list[GeneralFinancialData]) -> str:
        """Генерирует таблицу из полученной статистики"""
        if data:
            table_text = "```\n"

            table_text += "┌──────────────┬────────┬───────┐\n"
            table_text += "│Месяц         │Кол-во  │Сумма, │\n"
            table_text += "│              │занятий │руб.   │\n"
            table_text += "├──────────────┼────────┼───────┤\n"

            for dt in data:
                month = dt.month[:10].capitalize().ljust(12)
                volume = str(dt.volume).ljust(6)
                total = str(dt.total).ljust(5)
                table_text += f"│{month}  │{volume}  │{total}  │ \n"
                # table_text += "└────────────┴────────┴────────────────┘\n"
            table_text += "└──────────────┴────────┴───────┘\n"
            table_text += "```"
        else:
            table_text = 'В этом году занятий пока не было'

        return table_text

    def _get_months_list(self) -> list[str]:
        months_names = get_month_names(
                "wide", context="stand-alone", locale='ru_RU',
            )
        return list(months_names.values())

    def _get_months_dict(self) -> list[str]:
        months_names = get_month_names(
                "wide", context="stand-alone", locale='ru_RU',
            )
        return dict(months_names.items())

    async def _prepare_data_for_table(self, statistics: GeneralFinancialData, months_dict: dict) -> list[GeneralFinancialData]:
        total = [[months_dict[i], 0, 0] for i in range(1, 13)]

        for st in statistics:
            total[int(st.month) - 1][1] = st.volume
            total[int(st.month) - 1][2] = st.total

        logger.info('Подготовленный список для составления таблицы: %s', total)

        return [GeneralFinancialData(*i) for i in total]

    async def _get_general_statistics_for_the_year(self, conn, year) -> list[GeneralFinancialData]:
        """Получает статистику за год"""
        try:
            statistics = await get_general_statistics_for_the_year(conn, year)

            logger.info('Статистика за год: %s', statistics)

            if not statistics:
                return []

            return [GeneralFinancialData(*statistic) for statistic in statistics]

        except Exception as e:
            logger.exception("Ошибка получения статистики за год %s:", e)
            raise

    async def _get_general_sum_year(self, conn, year) -> int:
        """Получает общую сумму занятий за год"""
        try:
            total = await get_general_sum_year(conn, year)

            logger.info('Статистика за год: %s', total)

            if not total:
                return 0

            return int(*total)

        except Exception as e:
            logger.exception("Ошибка получения статистики за год %s:", e)
            raise


def create_general_financial_report(dialog_manager: DialogManager) -> GeneralFinancialReport:
    return GeneralFinancialReport(dialog_manager)
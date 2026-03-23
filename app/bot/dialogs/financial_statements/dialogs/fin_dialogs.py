from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start, Next, Back, Cancel, SwitchTo, Select, \
    Multiselect, ManagedMultiselect, ManagedCounter, Counter, Checkbox, Radio, ScrollingGroup, ListGroup, TimeSelect
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
import logging
from app.bot.dialogs import states
from pprint import pprint
from app.infrastructure.database.db import get_students, get_subject_stud, get_id_subject_stud, add_class_journal, \
    get_sum_price_week, get_sum_price_month
from psycopg import AsyncConnection
from operator import itemgetter
from app.bot.dialogs.common import MAIN_MENU_BUTTON
from typing import Any
from aiogram_dialog.widgets.style import Style
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
    today = datetime.now().date()
    start_end_week: tuple = await get_current_date_week(today)
    conn: AsyncConnection = dialog_manager.middleware_data.get('conn')
    sum_price_week = await get_sum_price_week(conn, *start_end_week)

    current_month = await get_current_date_month(today)
    print(current_month)
    sum_price_month = await get_sum_price_month(conn, current_month)

    return {'sum_price_week': sum_price_week[0] if sum_price_month else '0',
            'sum_price_month': sum_price_month[0]}


async def fin_report_month_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    pass


finpreview = Window(
    Format('В этом разделе вы можете отслеживать свои финансовые показатели '
           'в виде удобных схем и диаграмм, а также получать отчетность о количестве проведенных '
           'занятий и Ваших доходах за ближайшую неделю/месяц'),
    Column(
        Next(Const('Отчетность за неделю/месяц')),
        MAIN_MENU_BUTTON,
    ),
    getter=finpreview_getter,
    state=states.Finance.finpreview,
)

fin_report_week = Window(
    Format('Финансовый отчет за текущую неделю: \n'
           'Итоговый результат за неделю: <b>{sum_price_week} руб.</b> \n'
           'Итоговый результат за месяц: <b>{sum_price_month} руб.</b>'),
    Column(
        Back(Const('⬅️Назад')),
        MAIN_MENU_BUTTON,
    ),
    state=states.Finance.fin_report_week,
    getter=fin_report_week_getter,
)

fin_report = Window(
    Const('Выберете, за какой срок подготовить отчет'),
    Next(Const('Неделя')),
    SwitchTo(Const('Месяц'), id='SwitchTo_month', state=states.Finance.fin_report_month),
    getter=fin_report_getter,
    state=states.Finance.fin_report,
)

# fin_report_week = Window(
#     Format('Финансовый отчет за текущую неделю: '
#            'Итоговый результат за неделю: {sum_price_week}'),
#     state=states.Finance.fin_report_week,
#     getter=fin_report_week_getter,
# )

fin_report_month = Window(
    Format('Финансовый отчет за месяц: \n'
           'Итоговый результат за неделю: {sum_price_week}'),
    state=states.Finance.fin_report_month,
    getter=fin_report_month_getter,
)

finance = Dialog(
    finpreview,
    fin_report_week,
    fin_report,
    # fin_report_week,
    fin_report_month,
)

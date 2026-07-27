from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start, Next, Back, Cancel, SwitchTo, Select, \
    Multiselect, ManagedMultiselect, ManagedCounter, Counter, Checkbox, Radio, ScrollingGroup, ListGroup, TimeSelect
from aiogram_dialog.widgets.text import Const, Format
from app.bot.dialogs import states
from operator import itemgetter
from app.bot.dialogs.common import MAIN_MENU_BUTTON
from .fin_getters import finpreview_getter, fin_report_week_getter, fin_report_getter, fin_report_month_getter
from aiogram_dialog.widgets.style import Style


finpreview = Window(
    Format('В этом разделе вы можете отслеживать свои финансовые показатели '
           'в виде удобных схем и диаграмм, а также получать отчетность о количестве проведенных '
           'занятий и Ваших доходах за ближайшую неделю/месяц'),
    Column(
        SwitchTo(Const('Отчетность за неделю'), id='sw1', state=states.Finance.fin_report_week),
        SwitchTo(Const('Отчетность за месяц'), id='sw1', state=states.Finance.fin_report_month),
        SwitchTo(Const('Аналитика по месяцам'), id='sw1', state=states.Finance.fin_report_months),
        SwitchTo(Const('Аналитика за все время'), id='sw1', state=states.Finance.fin_all_time_report),
        MAIN_MENU_BUTTON,
    ),
    getter=finpreview_getter,
    state=states.Finance.finpreview,
)

fin_report_week = Window(
    Format('Финансовый отчет за текущую неделю: \n'
           'Итоговый результат за неделю: {sum_price_week}'),
    state=states.Finance.fin_report_week,
    getter=fin_report_week_getter,
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

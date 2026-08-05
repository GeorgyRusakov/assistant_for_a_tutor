from aiogram.enums import ParseMode
from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import Column, SwitchTo, Select, ScrollingGroup
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from app.bot.dialogs import states
from operator import itemgetter
from app.bot.dialogs.common import MAIN_MENU_BUTTON
from .fin_getters import finpreview_getter, fin_report_week_getter, fin_report_month_getter, get_year_getter, get_month_getter, \
                            select_fin_report_by_month_year_getter, fin_general_report_getter
from .fin_handlers import on_year_click, on_month_click, on_year_click_general_report
from aiogram_dialog.widgets.style import Style


finpreview = Window(
    Format('В этом разделе вы можете отслеживать свои финансовые показатели '
           'в виде удобных таблиц и диаграмм, а также получать отчетность о количестве проведенных '
           'занятий и Ваших доходах за ближайшую неделю/месяц или выбранный вами период'),
    Column(
        SwitchTo(Const('Текущая неделя'), id='sw1', state=states.Finance.fin_report_week),
        SwitchTo(Const('Текущий месяц'), id='sw2', state=states.Finance.fin_report_month),
        SwitchTo(Const('Выбрать период'), id='sw3', state=states.Finance.select_fin_report_by_year),
        SwitchTo(Const('Общая статистика'), id='sw4', state=states.Finance.select_general_fin_report_by_year),
        MAIN_MENU_BUTTON,
    ),
    getter=finpreview_getter,
    state=states.Finance.finpreview,
)

fin_report_week = Window(
    Format('Финансовый отчет за текущую ***неделю***: \n\n'
           '***Итоговый результат\: {sum_total_week} руб\.*** \n'),
    Format('***Общая статистика\:*** \n' \
           '{report_table}'),
    SwitchTo(Const('⬅️Назад'), id='st1', state=states.Finance.finpreview),
    MAIN_MENU_BUTTON,
    parse_mode=ParseMode.MARKDOWN_V2,
    state=states.Finance.fin_report_week,
    getter=fin_report_week_getter,
)

fin_report_month = Window(
    Format('Финансовый отчет за текущий ***месяц***: \n\n'
           '***Доход\: {sum_total_month} руб\.*** \n'),
    Format('***Статистика\:*** \n' \
           '{report_table}'),
    SwitchTo(Const('⬅️Назад'), id='st2', state=states.Finance.finpreview),
    MAIN_MENU_BUTTON,
    parse_mode=ParseMode.MARKDOWN_V2,
    state=states.Finance.fin_report_month,
    getter=fin_report_month_getter,
)

select_fin_report_by_year = Window(
    Const('За какой год хотите просмотреть отчет?'),
    ScrollingGroup(
        Select(
            Format("{item[0]}"),
            id='select_year',
            item_id_getter=itemgetter(0),
            items='year_row',
            on_click=on_year_click,
        ),
        width=1,
        height=5,
        id="scroll_with_pager_year",
    ),
    SwitchTo(Const('⬅️Назад'), id='st3', state=states.Finance.finpreview,),
    MAIN_MENU_BUTTON,
    state=states.Finance.select_fin_report_by_year,
    getter=get_year_getter,
)

select_fin_report_by_month = Window(
    Const('За какой месяц хотите просмотреть отчет? \n'),
    Const('Месяцы, в которые вы работали: '),
    ScrollingGroup(
        Select(
            Format("{item[1]}"),
            id='select_month',
            item_id_getter=itemgetter(0),
            items='months_list',
            on_click=on_month_click,
        ),
        width=1,
        height=5,
        id="scroll_with_pager_month",
    ),
    SwitchTo(Const('⬅️Назад'), id='st4', state=states.Finance.select_fin_report_by_year,),
    MAIN_MENU_BUTTON,
    state=states.Finance.select_fin_report_by_month,
    getter=get_month_getter,
)

select_fin_report_by_month_year = Window(
    Format('Финансовый отчет за ***{month_name}***: \n\n'
           '***Общий доход\: {sum_total_month} руб\.*** \n'),
    Format('***Статистика\:*** \n' \
           '{report_table}'),
    SwitchTo(Const('⬅️Назад'), id='st5', state=states.Finance.select_fin_report_by_month,),
    MAIN_MENU_BUTTON,
    parse_mode=ParseMode.MARKDOWN_V2,
    state=states.Finance.selected_fin_report_by_month_year,
    getter=select_fin_report_by_month_year_getter,
)

general_fin_report_by_year = Window(
    Const('За какой год хотите просмотреть отчет?'),
    ScrollingGroup(
        Select(
            Format("{item[0]}"),
            id='select_year',
            item_id_getter=itemgetter(0),
            items='year_row',
            on_click=on_year_click_general_report,
        ),
        width=1,
        height=5,
        id="scroll_with_pager_year",
    ),
    SwitchTo(Const('⬅️Назад'), id='st6', state=states.Finance.finpreview,),
    MAIN_MENU_BUTTON,
    state=states.Finance.select_general_fin_report_by_year,
    getter=get_year_getter,
)

select_general_fin_report = Window(
    Format('Финансовый отчет за *** {year} год***: \n\n'
           '***Общий доход\: {general_sum} руб\.*** \n'),
    Format('***Статистика\:*** \n' \
           '{report_table}'),
    StaticMedia(
        path="C:/Users/rusak/OneDrive/Рабочий стол/PythonProject/TelegramBots/TutorHelper/assistant_for_a_tutor/graphs/Статистика, 2026 г..png",
        type=ContentType.PHOTO,
    ),
    SwitchTo(Const('⬅️Назад'), id='st7', state=states.Finance.select_general_fin_report_by_year),
    MAIN_MENU_BUTTON,
    parse_mode=ParseMode.MARKDOWN_V2,
    state=states.Finance.fin_all_time_report,
    getter=fin_general_report_getter,
)

finance = Dialog(
    finpreview,
    fin_report_week,
    fin_report_month,
    select_fin_report_by_year,
    select_fin_report_by_month,
    select_fin_report_by_month_year,
    general_fin_report_by_year,
    select_general_fin_report
    # fin_report
)
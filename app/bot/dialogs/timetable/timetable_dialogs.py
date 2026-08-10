from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Column, Next, Back, Cancel, SwitchTo, Radio, ScrollingGroup, StubScroll, NumberedPager, TimeSelect
from aiogram_dialog.widgets.text import Const, Format
from app.bot.dialogs import states
from aiogram_dialog.widgets.text import Jinja
from pprint import pprint
from operator import itemgetter
from aiogram_dialog.widgets.style import Style
from .timetable_getters import timetable_preview_getter, timetable_view_getter, get_stud_getter, timetable_add_getter, input_time_getter, \
                                finish_timetable_getter, set_stud_default
from .timetable_handlers import hour_click, minute_click, sending_timetable_data


timetable_dlg = Dialog(
    # Окно выбора дейтсвия просмотра/добавления/удаления расписания
    Window(
        Format('{window_preview_timetable}'),
        Next(
            text=Const('Посмотреть расписание'),
            id="btn_add_timetable"
        ),
        SwitchTo(
            text=Const('Добавить/изменить расписание'),
            id="btn_view_timetable",
            state=states.Timetable.add_timetable_step_1
        ),
        Cancel(Const('⬅️Назад')),
        getter=timetable_preview_getter,
        state=states.Timetable.preview,
    ),
    # Окно просмотра расписания
    Window(
        Format('🗓{ru_day} \n'),
        Format('{timetable_text}'),
        # html_text,
        StubScroll(id='id_stub_scroll', pages=7),
        NumberedPager(scroll='id_stub_scroll', page_text=Format("{target_page1}\uFE0F\u20E3")),
        Back(Const('⬅️Назад')),
        parse_mode=ParseMode.MARKDOWN_V2,
        getter=timetable_view_getter,
        preview_data=timetable_view_getter,
        state=states.Timetable.view_timetable,
    ),
    # Выбираем ученика
    Window(
        Format('Выберете ученика'),
        ScrollingGroup(
            Radio(
                checked_text=Format("🔘 {item[0]}"),
                unchecked_text=Format("️⚪️ {item[0]}"),
                id="radio3_stud",
                item_id_getter=lambda x: x[1],
                items="stud_row",
                # on_click=radio3_click,
                # on_state_changed=radio3_click,
            ),
            width=1,
            height=5,
            id="scroll_with_pager",
        ),
        Row(
            Back(Const('⬅️Назад')),
            Next(Const('Следующий шаг➡️')),
        ),
        state=states.Timetable.add_timetable_step_1,
        getter=get_stud_getter,
    ),
    # Второе окно добавления расписания - выбираем день недели и нужный предмет
    Window(
        Format('Переходим к добавлению нового расписания. '
               'Для начала выберем нужный день недели и предмет (математика/физика), а также введите стоимость занятия'
               'с помощью специального счетчика'),
        Column(
            Radio(
                checked_text=Format('[✅] {item[1]}'),
                unchecked_text=Format('[ ] {item[1]}'),
                id='ch_subject',
                items='subjects',
                item_id_getter=lambda x: x[0],
                checked_style=Style("success"),
                # on_state_changed=selected_subject,
            ),
        ),
        Radio(
            checked_text=Format("✓ {item[1]}"),
            unchecked_text=Format("️ {item[1]}"),
            items="ru_day",
            item_id_getter=lambda x: x[0],
            id="radio2_day_week",
        ),
        Row(
            Back(Const('⬅️Назад')),
            Next(Const('Следующий шаг➡️')),
        ),
        state=states.Timetable.add_timetable_step_2,
        getter=timetable_add_getter
    ),
    # Вводим время занятия
    Window(
        Format('{input_time_text}'),
        TimeSelect(
            id='price_input',
            hour_header=Const('Часы'),
            minute_header=Const('Минуты'),
            on_hour_click=hour_click,
            on_minute_click=minute_click,
        ),
        Row(
            Back(Const('⬅️Назад')),
            Next(Const('Следующий шаг➡️')),
        ),
        state=states.Timetable.add_timetable_step_3,
        getter=input_time_getter,
    ),
    # Окно финальной проверки выбранных/введенных параметров
    Window(
        Format('Заключительный шаг - проверка введенных параметров'),
        Format('{finish_text}'),
        Button(
            Const('Отправить данные'), id='button_clicked', on_click=sending_timetable_data),
        state=states.Timetable.add_timetable_step_4,
        getter=finish_timetable_getter,
    ),
    on_start=set_stud_default,
)

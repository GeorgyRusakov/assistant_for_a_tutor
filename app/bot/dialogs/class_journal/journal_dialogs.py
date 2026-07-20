from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Column, Back,  SwitchTo, Select, Multiselect, \
    Checkbox, Radio, ScrollingGroup,\
    NumberedPager, FirstPage, PrevPage, CurrentPage, NextPage, LastPage
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.style import Style
from app.bot.dialogs import states
from operator import itemgetter
from app.bot.dialogs.common import MAIN_MENU_BUTTON
from .journal_getters import journal_preview_getter, get_stud_getter, product_getter, selected_student_getter, get_year_getter, \
    get_month_getter, get_classes_by_month_year_getter, view_card_getter
from .journal_handlers import on_student_click, date_button_next_clicked, date_button_prev_clicked, add_new_lesson, on_year_click, on_month_click, on_class_card_click

ID_SCROLL_NO_PAGER = "scroll_no_pager"

SCROLLS_MAIN_MENU_BUTTON = SwitchTo(
    text=Const("Back"),
    id="back",
    state=states.ClassJournal.preview,
    style=Style(style="primary"),
)

preview_journal = Window(
    Format('{window_preview_hello}'),
    Column(
        SwitchTo(
            text=Const('Проставить занятие'),
            id="btn_view_add_lesson",
            state=states.ClassJournal.add_lesson,
            ),
        SwitchTo(
            text=Const('Просмотреть журнал'),
            id="btn_view_jourmal",
            state=states.ClassJournal.journal_year,
            ),
        MAIN_MENU_BUTTON,
    ),
    getter=journal_preview_getter,
    state=states.ClassJournal.preview
)

add_lesson = Window(
    Format('{window_add_lesson_view}'),
    ScrollingGroup(
        Select(
            Format("{item[0]}"),
            id='select_student',
            item_id_getter=itemgetter(1),
            items='stud_row',
            on_click=on_student_click,
        ),
        width=1,
        height=5,
        id="scroll_with_pager",
    ),
    MAIN_MENU_BUTTON,
    state=states.ClassJournal.add_lesson,
    getter=get_stud_getter,
)

selected_student = Window(
    Format("Вы выбрали ученика: {selected_stud}"),
    Const("Добавляем занятие: "),
    Radio(
        checked_text=Format('[✅] {item[1]}'),
        unchecked_text=Format('[ ] {item[1]}'),
        id='radio1_subject',
        item_id_getter=lambda x: x[0],
        items='subjects',
        # on_click=radio1_click,
    ),
    Checkbox(
        unchecked_text=Const('[ ] Новое занятие'),
        checked_text=Const('[✅] Новое занятие'),
        id='checked_lesson',
        checked_style=Style("success"),
        default=True,
    ),
    Row(
        Button(text=Const('<'),
               id='date_button_prev',
               on_click=date_button_prev_clicked),
        Button(
            text=Format('{current_date}'),
            id='date_button',
        ),
        Button(text=Const('>'),
               id='date_button_next',
               on_click=date_button_next_clicked),
    ),
    # Calendar(
    #     id='calender',
    #     on_click=on_date_clicked,
    # ),
    Button(
        Const('Подтвержаем занятие'), id='button_new_lesson', on_click=add_new_lesson
    ),
    MAIN_MENU_BUTTON,
    getter=selected_student_getter,
    state=states.ClassJournal.selected_stud,
)

view_classes_by_year = Window(
    Const('За какой год хотите просмотреть журнал?'),
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
    SwitchTo(Const('⬅️Назад'), id='st', state=states.ClassJournal.preview),
    MAIN_MENU_BUTTON,
    state=states.ClassJournal.journal_year,
    getter=get_year_getter,

)

view_classes_by_month = Window(
    Const('За какой месяц хотите просмотреть журнал?'),
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
    Back(Const('⬅️Назад')),
    MAIN_MENU_BUTTON,
    state=states.ClassJournal.journal_month,
    getter=get_month_getter,
)


view_classes_by_month_year = Window(
    Const('Перед вами журнал занятий за выбранный период (месяц - год) \nKликайте на карточки занятий и смотрите более подробную информацию'),
    NumberedPager(
        scroll=ID_SCROLL_NO_PAGER,
        page_text=Format("{target_page1}\uFE0F\u20E3"),
        current_page_text=Format("{current_page1}"),
        current_page_style=Style(style="primary"),
    ),
    ScrollingGroup(
        Select(
            Format("{item[1]}"),
            id="ms",
            items="classes_dict",
            on_click = on_class_card_click,
            item_id_getter=itemgetter(0),
        ),
        width=1,
        height=5,
        hide_pager=True,
        id=ID_SCROLL_NO_PAGER,
    ),
    Row(
        FirstPage(
            scroll=ID_SCROLL_NO_PAGER, text=Format("⏮️ {target_page1}"),
        ),
        PrevPage(
            scroll=ID_SCROLL_NO_PAGER, text=Format("◀️"),
        ),
        CurrentPage(
            scroll=ID_SCROLL_NO_PAGER, text=Format("{current_page1}"),
        ),
        NextPage(
            scroll=ID_SCROLL_NO_PAGER, text=Format("▶️"),
        ),
        LastPage(
            scroll=ID_SCROLL_NO_PAGER, text=Format("{target_page1} ⏭️"),
        ),
    ),
    Column(
        Back(Const('⬅️Назад')),
        MAIN_MENU_BUTTON,
    ),
    getter=get_classes_by_month_year_getter,
    state=states.ClassJournal.journal_view,
)

view_class_card = Window(
    Format('{view_class_card}'),
    Column(
        Back(Const('⬅️Назад')),
        MAIN_MENU_BUTTON,
    ),
    getter=view_card_getter,
    state=states.ClassJournal.card_view,

)


journal_dialogs = Dialog(
    preview_journal,
    add_lesson,
    selected_student,
    view_classes_by_year,
    view_classes_by_month,
    view_classes_by_month_year,
    view_class_card
)
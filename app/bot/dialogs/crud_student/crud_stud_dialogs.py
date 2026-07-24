from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start, Next, Back, Cancel, SwitchTo, Select, \
    Multiselect, ManagedMultiselect, Counter, ManagedCounter, Radio, ListGroup, Checkbox, ManagedCheckbox, \
    ManagedListGroup, ManagedRadio, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput
from app.bot.dialogs import states
from pprint import pprint
from operator import itemgetter
from aiogram_dialog.widgets.style import Style
from app.bot.dialogs.common import MAIN_MENU_BUTTON
from .crud_stud_getters import get_text_stud_getter, window_add_stud_getter, get_grade, get_subject, delete_student_getter
from .crud_stud_handlers import name_check, correct_name_handler, error_age_handler, on_text_click, when_checked, sending_data, go_timetable, delete_students_handler


crud_student = Dialog(
    # Окно выбора добавления или удаления ученика
    Window(
        Format('{add_del_stud}'),
        Row(
            SwitchTo(Const('Добавить ученика'), id='first', state=states.AddDeleteStud.input_name),
            SwitchTo(Const('Удалить ученика'), id='second', state=states.AddDeleteStud.delete),
        ),
        MAIN_MENU_BUTTON,
        getter=get_text_stud_getter,
        state=states.AddDeleteStud.select_opt,
    ),
    # Окно ввода имени ученика
    Window(
        Format('{window_add_stud}'),
        TextInput(
            id='name_input',
            type_factory=name_check,
            on_success=correct_name_handler,
            on_error=error_age_handler,
        ),
        SwitchTo(Const('⬅️Отмена'), id='first', state=states.AddDeleteStud.select_opt),
        # parse_mode='Markdown',
        state=states.AddDeleteStud.input_name,
        getter=window_add_stud_getter,
    ),
    # Окно выбора класса ученика
    Window(
        Format('{select_grade_sub_price_stud}'),
        Group(
            Column(
                Radio(
                    id='grade',
                    checked_text=Format('[✅] {item[0]}'),
                    unchecked_text=Format('[ ] {item[0]}'),
                    item_id_getter=lambda x: x[1],
                    items='grades',
                    # on_click=grade_selection,
                    checked_style=Style("success")
                ),
            ),
            width=2
        ),
        Next(Const('Следующий шаг➡️')),
        SwitchTo(Const('⬅️Отмена'), id='first', state=states.AddDeleteStud.select_opt),
        state=states.AddDeleteStud.select_grade,
        getter=get_grade,
    ),
    # Окно ввода стоимости занятия, выбора предмета ученика
    Window(
        Const('Выберете предметы и с помощью специального счетчика введите стоимость занятия (занятий).'),
        ListGroup(
            Column(
                Checkbox(
                    checked_text=Format('[✅] {item[0]}'),
                    unchecked_text=Format('[ ] {item[0]}'),
                    id='ch_subject',
                    checked_style=Style("success"),
                    # on_state_changed=selected_subject,
                ),
            ),
            Counter(
                default=1000,
                increment=100,
                id='go_price_input',
                text=Format("{value} руб."),
                on_text_click=on_text_click,
                when=when_checked,
            ),
            id='lg',
            item_id_getter=lambda x: x[1],
            items='subjects',
        ),
        Back(Const('⬅️Назад')),
        Button(Const('Добавить ученика'), id='button_clicked', on_click=sending_data, style=Style("success")),
        Button(Const('Расписание'), id='go_timetable_button', on_click=go_timetable, style=Style("success")),
        SwitchTo(Const('⬅️Отмена'), id='first', state=states.AddDeleteStud.select_opt),
        state=states.AddDeleteStud.select_subject,
        getter=get_subject,
    ),
    # Окно удаления ученика
    Window(
        Format('{window_del_stud}'),
        ScrollingGroup(
            Multiselect(
                checked_text=Format("✓ {item.name}"),
                unchecked_text=Format("{item.name}"),
                checked_style=Style(style="primary"),
                # unchecked_style=Style(style="primary"),
                id="multi",
                items='lst_students',
                item_id_getter=lambda x: x.id,
            ),
            width=1,
            height=7,
            id="scroll_with_pager",
        ),
            Button(
                text=Const("Удалить"),
                id="delete_students",
                on_click=delete_students_handler,
                style=Style(style="danger"),
            ),
        SwitchTo(Const('⬅️Отмена'), id='first', state=states.AddDeleteStud.select_opt),
        state=states.AddDeleteStud.delete,
        getter=delete_student_getter,
    ),
)
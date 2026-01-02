from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start
from aiogram_dialog.widgets.text import Const, Format
from environs import Env
from . import states


async def button_clicked():
    pass


async def get_text_main_menu(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'menu': local['menu']}


main_menu = Dialog(
    Window(
        Format('{menu}'),
        Group(
            Column(
                Button(
                    text=Const('🧮 Журнал занятий'),
                    id='button_1',
                    on_click=button_clicked),
                Button(
                    text=Const('📊📈 Фин. отчетность'),
                    id='button_2',
                    on_click=button_clicked),
            ),
            Row(
                Start(
                    text=Const('🆕 Добавление/удаление учеников'),
                    id='go_second_dialog',
                    state=states.AddDeleteStud.select_opt),
                Button(
                    text=Const('📆🕒 Расписание занятий'),
                    id='button_2',
                    on_click=button_clicked),
                Button(
                    text=Const('📌📝 Заметки по ученикам'),
                    id='button_3',
                    on_click=button_clicked),
            ),
            width=2,
        ),
        getter=get_text_main_menu,
        state=states.StartWork.menu,
    ),
)


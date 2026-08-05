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
                Start(
                    text=Const('🧮 Журнал занятий'),
                    id='go_journal_dialog',
                    state=states.ClassJournal.preview),
                Start(
                    text=Const('📊📈 Отчетность'),
                    id='button_2',
                    state=states.Finance.finpreview),
            ),
            Row(
                Start(
                    text=Const('👨‍🎓👩‍🎓 Студенты'),
                    id='go_add_dialog',
                    state=states.AddDeleteStud.select_opt),
                Start(
                    text=Const('📆🕒 Расписание'),
                    id='go_timetable_dialog',
                    state=states.Timetable.preview),
                Button(
                    text=Const('📌📝 Заметки'),
                    id='button_3',
                    on_click=button_clicked),
            ),
            width=2,
        ),
        getter=get_text_main_menu,
        state=states.StartWork.menu,
    ),
)

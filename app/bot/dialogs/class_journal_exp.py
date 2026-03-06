from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start, Next, Back, Cancel, SwitchTo, Select, \
    Multiselect, ManagedMultiselect, ManagedCounter, Counter, Checkbox, Radio, ScrollingGroup, ListGroup
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
import logging
from . import states
from pprint import pprint
from app.infrastructure.database.db import get_students
from psycopg import AsyncConnection
from operator import itemgetter

logger = logging.getLogger(__name__)


async def get_stud_getter(dialog_manager: DialogManager,  local: dict, conn: AsyncConnection, **kwargs):
    stud_row = await get_students(conn)
    # print(stud_row)
    lst_stud = [(f'{i[1]}', i[0]) for i in stud_row]
    # pprint(lst_stud)
    return {'stud_row': lst_stud,
            'len_stud_row': len(stud_row),
            'window_journal_view': local['window_journal_view']}


async def journal_show(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()


async def on_click(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=states.StartWork.menu)


async def on_text_click(
        event: CallbackQuery,
        widget: ManagedCounter,
        dialog_manager: DialogManager
) -> None:
    print(widget.widget.text)
    print(event.answer(f"Value: {widget.get_value()}"))
    await event.answer(f"Value: {widget.get_value()}")


async def journal_preview_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'window_preview_hello': local['window_preview_hello']}


class_journal = Dialog(
    Window(
        Format('{window_preview_hello}'),
        Button(
            text=Const('Посмотреть журнал'),
            id="btn",
            on_click=journal_show
        ),
        Cancel(Const('⬅️Назад')),
        getter=journal_preview_getter,
        state=states.ClassJournal.preview
    ),
    Window(
        Format('{window_journal_view}'),
        ScrollingGroup(
            ListGroup(
                Counter(
                    default=0,
                    id='go',
                    text=Format("{data[item][0]}: {value}"),
                    on_text_click=on_text_click,
                ),
                id="ms",
                items="stud_row",
                item_id_getter=itemgetter(1),
            ),
            width=3,
            height=5,
            id="scroll_with_pager",
        ),
        Button(
            text=Const('⬅️Вернуться в меню'),
            id="btn1",
            on_click=on_click
        ),
        state=states.ClassJournal.journal,
        getter=get_stud_getter,
    ),
)

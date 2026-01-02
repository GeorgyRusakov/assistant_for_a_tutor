from aiogram.filters import CommandStart
from aiogram import Router
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group
from aiogram_dialog.widgets.text import Const, Format
from . import states


user_router = Router()


async def go_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()


async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def go_second_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=states.StartWork.menu)


async def common_getter(dialog_manager: DialogManager, event_from_user: User, local: dict, **kwargs):
    return {'username': event_from_user.username,
            'start_text': local['/start'],
            'help_text': local['/help']}


start_dialog = Dialog(
    Window(
        Format(text='Привет, <b>{username}</b>!\n'),
        Format('{start_text}'),
        Row(
            Button(text=Const('👨‍💻 Начало работы'), id='begin', on_click=go_second_dialog),
            Button(text=Const('ℹ️ О боте'), id='inf', on_click=go_next),
        ),
        state=states.StartSG.start,
    ),
    Window(
        Format('{help_text}'),
        Group(
            Column(
                Button(
                    text=Const('⬅️Назад'),
                    id='button_1',
                    on_click=go_back),
            ),
        ),
        state=states.StartSG.helper
    ),
    getter=common_getter
)


@user_router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.StartSG.start,
        mode=StartMode.RESET_STACK,
    )

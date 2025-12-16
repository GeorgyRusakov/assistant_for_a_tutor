from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import (
    BaseDialogManager,
    Dialog,
    DialogManager,
    StartMode,
    Window,
    ShowMode
)
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Multi, Progress, Format
from aiogram import Router


user_router = Router()


class StartSG(StatesGroup):
    window_1 = State()


async def username_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):

    getter_data = {'username': event_from_user.username or 'Stranger'}
    # print(dialog_manager.start_data)
    a = dialog_manager.start_data.get('local')
    # dialog_manager.dialog_data['local'] = local.get("/start")
        # dialog_manager.start_data.clear()
    return {'local': a}


start_dialog = Dialog(
    Window(
        Format('{local}'),
        getter=username_getter,
        state=StartSG.window_1
    ),
)


@user_router.message(Command('start'))
async def command_start_process(message: Message, local, dialog_manager: DialogManager):

    await dialog_manager.start(
        state=StartSG.window_1,
        mode=StartMode.RESET_STACK,
        data={'local': local.get('/start')}
    )

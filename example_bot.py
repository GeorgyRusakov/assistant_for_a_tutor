from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group
from aiogram_dialog.widgets.text import Const, Format
from environs import Env
from app.locale.ru import RU
from pprint import pprint


env = Env()
env.read_env()

BOT_TOKEN = env('BOT_TOKEN')

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

router = Router()


class StartSG(StatesGroup):
    start = State()
    second = State()


class StartWork(StatesGroup):
    begin = State()


async def go_back(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.back()


async def go_next(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()


async def go_second_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartWork.begin)


# Это геттер
async def get_username(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    # pprint(dialog_manager.dialog_data.get())
    return {'username': event_from_user.username}


async def get_text_main_menu(dialog_manager, **kwargs):
    return {'menu': RU['menu']}


async def button_clicked():
    pass

start_dialog = Dialog(
    Window(
        Format(text='Привет, <b>{username}</b>!\n'),
        Const(
            text=RU['/start']
        ),
        Row(
            Button(text=Const('👨‍💻 Начало работы'), id='begin', on_click=go_second_dialog),
            Button(text=Const('ℹ️ О боте'), id='inf', on_click=go_next),
        ),
        getter=get_username,
        state=StartSG.start,
    ),
    Window(
        Const(RU['/help']),
        Group(
            Column(
                Button(
                    text=Const('⬅️Назад'),
                    id='button_1',
                    on_click=go_back),
            ),
        ),
        state=StartSG.second
    )
)

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
                Button(
                    text=Const('🆕 Добавление/удаление учеников'),
                    id='button_1',
                    on_click=button_clicked),
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
        state=StartWork.begin,
    ),
)


# Это классический хэндлер, который будет срабатывать на команду /start
@router.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)


dp.include_router(router)
dp.include_router(start_dialog)
dp.include_router(main_menu)
setup_dialogs(dp)
dp.run_polling(bot)
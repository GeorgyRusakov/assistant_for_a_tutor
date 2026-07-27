from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, SubManager
from aiogram_dialog.widgets.kbd import Button, ManagedCounter, ManagedCheckbox
from aiogram_dialog.widgets.input import ManagedTextInput
import logging
from app.bot.dialogs import states
from pprint import pprint
from app.infrastructure.database.db import delete_students
from ...services.student_service import create_student_service

logger = logging.getLogger(__name__)


def when_checked(data: dict, widget, manager: SubManager) -> bool:
    check_button: ManagedCheckbox = manager.find('ch_subject')
    return check_button.is_checked()

async def on_text_click(
        event: CallbackQuery,
        widget: ManagedCounter,
        dialog_manager: DialogManager
) -> None:
    await event.answer("Cтавь побольше!😁")

def name_check(text: str) -> str:
    if text.replace(" ", "").isalpha() and len(text) < 50:
        return text
    raise ValueError

async def error_age_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(text='Упс, вы ввели некорректное имя... Попробуйте ещё раз')

async def correct_name_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        name: str) -> None:
    dialog_manager.dialog_data.update(context_stud=[name])

    await message.answer(text=f'Отлично, имя нового ученика - {name}. Переходим к следующему действию')
    await dialog_manager.next()


async def correct_price_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        price: str) -> None:
    dialog_manager.dialog_data['context_stud'].append(int(price))
    await message.answer(text='Супер, переходим к выбору предмета ученика')
    await dialog_manager.next()


async def go_timetable(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    service = create_student_service(dialog_manager)

    student_data = service.extract_student_data()

    await service.save_student(student_data)

    await dialog_manager.start(state=states.Timetable.add_timetable_step_2, data=(student_data.name, student_data.grade))


async def sending_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    service = create_student_service(dialog_manager)

    student_data = service.extract_student_data()

    await service.save_student(student_data)

    await callback.message.answer(text='Данные отправлены на сервер! Возвращаемся в основное меню')
    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)


async def delete_students_handler(callback: CallbackQuery, button: Button, manager: DialogManager):
    student_checked: list = manager.find('multi').get_checked()
    logger.info('Список студентов на удаление: %s и тип: %s', student_checked, type(student_checked))

    if not student_checked:
        await callback.answer('Выберете хотя бы одного ученика для удаления!')
        return

    student_checked = list(map(int, student_checked))

    try:
        conn = manager.middleware_data.get('conn')

        await delete_students(conn, student_checked)

        await callback.answer('Студент(ы) успешно удалены!')

        logger.info("Студенты успешно удалены")

        await manager.switch_to(state=states.AddDeleteStud.select_opt)

    except Exception as e:
        logger.exception('Ошибка при попытке удаления студентов: %s', e)

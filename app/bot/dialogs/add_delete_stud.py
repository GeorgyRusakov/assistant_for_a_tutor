from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start, Next, Back, Cancel, SwitchTo, Select, \
    Multiselect, ManagedMultiselect
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
import logging
from . import states
from pprint import pprint
from app.infrastructure.database.db import add_student

logger = logging.getLogger(__name__)


def name_check(text: str) -> str:
    if all(ch.isalpha() for ch in text) and len(text) < 40:
        return text
    raise ValueError


def price_check(text: str) -> str:
    if all(ch.isdigit() for ch in text) and int(text) < 10000:
        return text
    raise ValueError


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
    await message.answer(text=f'Супер, переходим к выбору предмета ученика')
    await dialog_manager.next()


async def error_price_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(text='Наверное переборщил с нулями😁 или добавил букву, повнимательнее')


async def error_age_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(text='Упс, вы ввели некорректное имя... Попробуйте ещё раз')


async def grade_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    lst_grade_stud = dialog_manager.dialog_data.get('lst_grade')  # Получаем список классов

    for grade, grade_id in lst_grade_stud:
        if grade_id == int(item_id):
            dialog_manager.dialog_data['context_stud'].append(grade)
            break

    await callback.message.answer(text=f'Хорошо, ученик в {item_id} классе. Движемся дальше!')
    await dialog_manager.next(show_mode=ShowMode.DELETE_AND_SEND)


async def get_grade(dialog_manager: DialogManager, local: dict, **kwargs):
    grade = [
        ('1-4 класс', 1),
        ('5 класс', 5),
        ('6 класс', 6),
        ('7 класс', 7),
        ('8 класс', 8),
        ('9 класс', 9),
        ('10 класс', 10),
        ('11 класс', 11),
    ]
    dialog_manager.dialog_data.update(lst_grade=grade)
    return {'grades': grade,
            'select_grade_stud': local['select_grade_stud']}


async def get_subject_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    subjects = [
        ('Математика', '1'),
        ('Физика', '2'),
    ]
    if dialog_manager.dialog_data.get('lst_subject') is None:
        dialog_manager.dialog_data.update(lst_subject=subjects)
    return {"subjects": subjects,
            "select_subject_stud": local['select_subject_stud']}


async def get_text_stud_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'add_del_stud': local['add_del_stud']}


async def window_add_stud_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'window_add_stud': local['window_add_stud']}


async def input_price_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'input_price': local['input_price']}


async def sending_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    widget = dialog_manager.find('multi_subject')  # Находим нужный виджет(мультиселект)
    select_sub = widget.get_checked()  # Получаю список выбранных предметов(id)
    multi_select = dialog_manager.dialog_data.get('lst_subject')  # Получаю общий список предметов(предмет, id)

    # Получаем названия выбранных предметов
    select_subject = [multi_select[i][0] for i in range(len(multi_select)) if multi_select[i][1] in select_sub]

    dialog_manager.dialog_data['context_stud'].append(select_subject)  # Записываем полученные значения в словарь

    name, grade, price, subject = dialog_manager.dialog_data.get('context_stud')

    conn = dialog_manager.middleware_data.get('conn')

    logger.info('Записываем данные в бд')
    await add_student(conn, name=name, grade=grade, price=price,
                      subject=' '.join(subject))

    await callback.message.answer(text=f'Данные отправлены на сервер! Возвращаемся в основное меню')
    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)


add_del_stud = Dialog(
    # Окно выбора добавления или удаления ученика
    Window(
        Format('{add_del_stud}'),
        Row(
            SwitchTo(Const('Добавить ученика'), id='first', state=states.AddDeleteStud.input_name),
            SwitchTo(Const('Удалить ученика'), id='second', state=states.AddDeleteStud.delete),
        ),
        Cancel(text=Const('Меню')),
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
        SwitchTo(Const('Назад'), id='first', state=states.AddDeleteStud.select_opt),
        state=states.AddDeleteStud.input_name,
        getter=window_add_stud_getter,
    ),
    # Окно выбора класса ученика
    Window(
        Format('{select_grade_stud}'),
        Column(
            Select(
                Format('{item[0]}'),
                id='grade',
                item_id_getter=lambda x: x[1],
                items='grades',
                on_click=grade_selection,
            ),
        ),
        state=states.AddDeleteStud.select_grade,
        getter=get_grade,
    ),
    # Окно ввода стоимости занятия
    Window(
        Format('{input_price}'),
        TextInput(
            id='price_input',
            type_factory=price_check,
            on_success=correct_price_handler,
            on_error=error_price_handler,
        ),
        # SwitchTo(Const('Назад'), id='first', state=states.AddDeleteStud.select_opt),
        state=states.AddDeleteStud.input_price,
        getter=input_price_getter,
    ),
    # Окно выбора предта(ов)
    Window(
        Format('{select_subject_stud}'),
        Column(
            Multiselect(
                checked_text=Format('[✅] {item[0]}'),
                unchecked_text=Format('[ ] {item[0]}'),
                id='multi_subject',
                item_id_getter=lambda x: x[1],
                items='subjects',
                # on_state_changed=selected_subject,
            ),
            Button(
                Const('Отправить данные'), id='button_clicked', on_click=sending_data)
        ),
        state=states.AddDeleteStud.select_subject,
        getter=get_subject_getter,
    ),
    # Окно удаления ученика
    Window(
        Const('Удаление ученика'),
        SwitchTo(Const('Назад'), id='first', state=states.AddDeleteStud.select_opt),
        state=states.AddDeleteStud.delete,
    ),
)

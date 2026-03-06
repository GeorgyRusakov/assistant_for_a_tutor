from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode, SubManager
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start, Next, Back, Cancel, SwitchTo, Select, \
    Multiselect, ManagedMultiselect, Counter, ManagedCounter, Radio, ListGroup, Checkbox, ManagedCheckbox, \
    ManagedListGroup, ManagedRadio
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
import logging
from . import states
from pprint import pprint
from app.infrastructure.database.db import add_student, get_context_last_id_stud, add_subject_students
from aiogram_dialog.widgets.style import Style

logger = logging.getLogger(__name__)


def name_check(text: str) -> str:
    if all(ch.isalpha() for ch in text) and len(text) < 40:
        return text
    raise ValueError


async def on_text_click(
        event: CallbackQuery,
        widget: ManagedCounter,
        dialog_manager: DialogManager
) -> None:
    await event.answer(f"Что так мало? Не мелочись, ставь побольше!😁🤑")


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


async def error_age_handler(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError):
    await message.answer(text='Упс, вы ввели некорректное имя... Попробуйте ещё раз')


# async def grade_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
#     lst_grade_stud = dialog_manager.dialog_data.get('lst_grade')  # Получаем список классов
#
#     for grade, grade_id in lst_grade_stud:
#         if grade_id == int(item_id):
#             dialog_manager.dialog_data['context_stud'].append(grade)
#             break
#
#     await callback.message.answer(text=f'Хорошо, ученик в {item_id} классе. Движемся дальше!')
#     await dialog_manager.next(show_mode=ShowMode.DELETE_AND_SEND)


async def get_subject(dialog_manager: DialogManager, local: dict, **kwargs):
    subjects = [
        ('Математика', '1'),
        ('Физика', '2'),
    ]

    if dialog_manager.dialog_data.get('lst_subject') is None:
        dialog_manager.dialog_data.update(lst_subject=subjects)

    return {"subjects": subjects, }


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

    if dialog_manager.dialog_data.get('lst_grade') is None:
        dialog_manager.dialog_data.update(lst_grade=grade)

    return {'grades': grade,
            'select_grade_sub_price_stud': local['select_grade_sub_price_stud'], }


async def get_text_stud_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'add_del_stud': local['add_del_stud']}


async def go_timetable(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    context_stud = await send_stud_db(dialog_manager)
    await dialog_manager.start(state=states.Timetable.add_timetable_step_2, data=context_stud)


async def window_add_stud_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'window_add_stud': local['window_add_stud']}


def when_checked(data: dict, widget, manager: SubManager) -> bool:
    # pprint(data)
    check_button: ManagedCheckbox = manager.find('ch_subject')
    return check_button.is_checked()


async def send_stud_db(dialog_manager: DialogManager):
    name_input_widget: ManagedTextInput = dialog_manager.find('name_input')
    name_stud = name_input_widget.get_value()  # Получаем введенное имя ученика

    grade_radio_widget: ManagedRadio = dialog_manager.find('grade')  # Получаем виджет радио кнопки
    grade_stud_item_id = grade_radio_widget.get_checked()  # Получаем id выбранной кнопки
    lst_grade_stud = dialog_manager.dialog_data.get('lst_grade')  # Получаем общий список классов
    grade_stud = None  # Класс ученика
    for grade, grade_id in lst_grade_stud:
        if grade_id == int(grade_stud_item_id):
            grade_stud = grade
            break

    lg: ManagedListGroup = dialog_manager.find('lg')  # Получаем виджет listgroup кнопки
    lst_subject = dialog_manager.dialog_data.get('lst_subject')  # Получаем список предметов
    id_price_select_subject = []  # Список id выбранных предметов, а также цену занятия за каждый предмет
    for sub, id in lst_subject:
        checkbox: ManagedCheckbox = lg.find_for_item('ch_subject', str(id))
        if checkbox.is_checked():
            counter: ManagedCounter = lg.find_for_item('go_price_input', str(id))
            price = counter.get_value()
            id_price_select_subject.append([id, price])

    conn = dialog_manager.middleware_data.get('conn')

    logger.info('Записываем данные в таблицу students')
    context_id_stud: tuple = await add_student(conn, name=name_stud, grade_stud=grade_stud)

    # context_id_stud = await get_context_last_id_stud(conn, name_stud, grade_stud)

    logger.info('Записываем данные в таблицу subject_students')
    for id, price in id_price_select_subject:
        await add_subject_students(conn, id, context_id_stud[0], price)  # Записываем данные в таблицу subject_students

    return [name_stud, grade_stud]


async def sending_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await send_stud_db(dialog_manager)

    await callback.message.answer(text=f'Данные отправлены на сервер! Возвращаемся в основное меню')
    await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)


# async def selected_subject(event, source, dialog_manager: DialogManager, **kwargs):
#     print(event)
#     print(source)
#     lg: ManagedListGroup = dialog_manager.find('lg')
#     print(lg.widget.i)


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
    # Окно выбора класса ученика, ввода стоимости занятия, выбора предмета ученика
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
        state=states.AddDeleteStud.select_grade,
        getter=get_grade,
    ),
    Window(
        Format('Выберете предметы и с помощью специального счетчика введите стоимость занятия (занятий).'),
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
        state=states.AddDeleteStud.select_subject,
        getter=get_subject,
    ),
    # Окно удаления ученика
    Window(
        Const('Удаление ученика'),
        SwitchTo(Const('⬅️Назад'), id='first', state=states.AddDeleteStud.select_opt),
        state=states.AddDeleteStud.delete,
    ),
)

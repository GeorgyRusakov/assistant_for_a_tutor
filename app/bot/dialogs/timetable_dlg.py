from babel.dates import get_day_names
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, ShowMode, SubManager
from aiogram_dialog.widgets.kbd import Button, Row, Column, Group, Start, Next, Back, Cancel, SwitchTo, Select, \
    Multiselect, ManagedMultiselect, Checkbox, Radio, ScrollingGroup, ListGroup, StubScroll, NumberedPager, \
    ManagedRadio, Counter, ManagedCheckbox, ManagedCounter, TimeSelect
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
import logging
from . import states
from pprint import pprint
from app.infrastructure.database.db import get_students, add_timetable, get_timetable, get_context_last_id_stud, \
    get_subject_stud
from psycopg import AsyncConnection
from operator import itemgetter
from aiogram_dialog.widgets.style import Style
import re

logger = logging.getLogger(__name__)


async def input_time_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'input_time_text': local['input_time_text']}


# async def correct_time_handler(
#         message: Message,
#         widget: ManagedTextInput,
#         dialog_manager: DialogManager,
#         price: str) -> None:
#     # dialog_manager.dialog_data['context_stud'].append(int(price))
#     await message.answer(text=f'Супер, время корректно, переходим к завершающему шагу')
#     await dialog_manager.next()


async def timetable_preview_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    # Сразу добавляем словарь дней недели в dialog_data
    if dialog_manager.dialog_data.get('ru_day_dict') is None:
        await lst_subject_add_data(dialog_manager)

    return {'window_preview_timetable': local['window_preview_timetable']}


async def timetable_view_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    current_page = await dialog_manager.find('id_stub_scroll').get_page()
    conn: AsyncConnection = dialog_manager.middleware_data.get('conn')
    ru_day_dict = dialog_manager.dialog_data.get('ru_day_dict')
    day_week = ru_day_dict.get(current_page)
    timetable = await get_timetable(conn=conn, day_week=day_week)
    # print(timetable)
    timetable_text = ''
    if timetable is not None:
        for i in timetable:
            timetable_text += f'Ученик: {i[0]} \n' \
                              f'Предмет: {i[1]} \n' \
                              f'Время: {i[3]} \n\n'
    else:
        timetable_text += 'В этот день занятий нет'
    # ru_day = get_day_names('wide', locale='ru_Ru')
    return {'ru_day': day_week,
            'timetable_text': timetable_text}


# async def radio3_click(event: CallbackQuery,
#                        widget: ManagedRadio,
#                        dialog_manager: DialogManager,
#                        item_id: str) -> None:
#     print(widget.get_checked())
#     print(item_id)

async def lst_subject_add_data(
        dialog_manager: DialogManager):  # Функция добавления сокращенных дней недели в dialog_data
    ru_day_wide = get_day_names('wide', locale='ru_RU')
    ru_day_dict_wide = dict(ru_day_wide)
    dialog_manager.dialog_data.update(ru_day_dict=ru_day_dict_wide)


async def finish_timetable_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    radio1_subject = dialog_manager.find(
        'ch_subject').get_checked()  # Получаем данные с нажатой кнопки по предмету

    radio2_day_week = dialog_manager.find('radio2_day_week').get_checked()  # Нажатая кнопка дня недели

    radio3_stud = dialog_manager.find('radio3_stud').get_checked()  # Нажатая кнопка по ученику

    # time_input = dialog_manager.find('price_input').get_value()  # Получаем введенное время занятия
    time_hour = dialog_manager.dialog_data.get('time_hour')
    time_minute = dialog_manager.dialog_data.get('time_minute')
    input_time = f'{time_hour}:{time_minute}'

    lst_stud = []  # Если начинаем добавлять расписание из окна добавления
    # ученика, то список студентов не загружается в dialog_data
    if dialog_manager.dialog_data.get('lst_stud') is None:
        conn = dialog_manager.middleware_data.get('conn')
        stud_row = await get_students(conn)
        lst_stud = [(f'{i[1]}', i[0]) for i in stud_row]
    else:
        lst_stud = dialog_manager.dialog_data.get('lst_stud')

    if dialog_manager.dialog_data.get('ru_day_dict') is None:
        await lst_subject_add_data(dialog_manager)

    lst_subject = dialog_manager.dialog_data.get('lst_subject')
    print(lst_subject)
    ru_day_dict = dialog_manager.dialog_data.get('ru_day_dict')

    name_stud = [lst_stud[i][0] for i in range(len(lst_stud)) if lst_stud[i][1] == int(radio3_stud)]
    subject = [lst_subject[i][1] for i in range(len(lst_subject)) if lst_subject[i][0] == int(radio1_subject)]
    day_week = ru_day_dict.get(int(radio2_day_week))

    dialog_manager.dialog_data.update(contex_timetable=[radio3_stud, radio1_subject, day_week, input_time])

    finish_text = f'Предмет: {subject[0]} \n' \
                  f'День недели: {day_week} \n' \
                  f'Время: {input_time} \n' \
                  f'Ученик: {name_stud[0]} \n'

    return {'finish_text': finish_text}


async def sending_timetable_data(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    conn: AsyncConnection = dialog_manager.middleware_data.get('conn')
    context_timetable = dialog_manager.dialog_data.get('contex_timetable')
    logger.info('Записываем данные в бд')
    await add_timetable(conn, *context_timetable)

    await callback.message.answer(text=f'Данные отправлены на сервер! Возвращаемся в основное меню')
    await dialog_manager.start(state=states.StartWork.menu, show_mode=ShowMode.DELETE_AND_SEND)


async def timetable_add_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    subjects = []
    conn: AsyncConnection = dialog_manager.middleware_data.get('conn')

    if dialog_manager.dialog_data.get('current_id_stud') is not None:

        current_id_stud = dialog_manager.dialog_data.get('current_id_stud')
        subjects = await get_subject_stud(conn, current_id_stud)
        print(subjects)
    else:
        logger.info('id ученика не найден, список предметов не получен')

    if not subjects:
        subjects = [
            (1, 'Математика'),
            (2, 'Физика'),
        ]

    ru_day_abbreviated = get_day_names('abbreviated', locale='ru_Ru')

    ru_day_dict_abbrev = dict(ru_day_abbreviated)

    if dialog_manager.dialog_data.get('lst_subject') is None:
        dialog_manager.dialog_data.update(lst_subject=subjects)

    return {"subjects": subjects,
            "ru_day": ru_day_dict_abbrev.items()}


def when_checked(data: dict, widget, manager: SubManager) -> bool:
    # pprint(data)
    check_button: ManagedCheckbox = manager.find('ch_subject')
    return check_button.is_checked()


async def on_text_click(
        event: CallbackQuery,
        widget: ManagedCounter,
        dialog_manager: DialogManager
) -> None:
    await event.answer(f"Что так мало? Не мелочись, ставь побольше!😁🤑")


async def set_stud_default(_, dialog_manager: DialogManager):
    context_stud: list = []

    if dialog_manager.start_data is not None:
        context_stud = dialog_manager.start_data

        conn: AsyncConnection = dialog_manager.middleware_data.get('conn')
        id_stud = await get_context_last_id_stud(conn, *context_stud)

        print(dialog_manager.start_data)

        if id_stud is not None:
            dialog_manager.dialog_data.update(current_id_stud=id_stud[0])
            radio_stud: ManagedRadio = dialog_manager.find('radio3_stud')
            await radio_stud.set_checked(str(id_stud[0]))


async def hour_click(callback: CallbackQuery, counter, dialog_manager: DialogManager, value):
    dialog_manager.dialog_data.update(time_hour=value)
    print(value)


async def minute_click(callback: CallbackQuery, counter, dialog_manager: DialogManager, value):
    dialog_manager.dialog_data.update(time_minute=value)
    print(value)


async def get_stud_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    stud_row = await get_students(conn)
    # print(stud_row)
    # print(dialog_manager.start_data)
    lst_stud = [(f'{i[1]}', i[0]) for i in stud_row]
    dialog_manager.dialog_data.update(lst_stud=lst_stud)
    return {'stud_row': lst_stud,
            'len_stud_row': len(stud_row),
            'window_journal_view': local['window_journal_view']}


timetable_dlg = Dialog(
    # Окно выбора дейтсвия просмотра/добавления/удаления расписания
    Window(
        Format('{window_preview_timetable}'),
        Next(
            text=Const('Посмотреть расписание'),
            id="btn_add_timetable"
        ),
        SwitchTo(
            text=Const('Добавить/изменить расписание'),
            id="btn_view_timetable",
            state=states.Timetable.add_timetable_step_1
        ),
        Cancel(Const('⬅️Назад')),
        getter=timetable_preview_getter,
        state=states.Timetable.preview,
    ),
    # Окно просмотра расписания
    Window(
        Format('День недели: {ru_day} \n'),
        Format('{timetable_text}'),
        StubScroll(id='id_stub_scroll', pages=7),
        NumberedPager(scroll='id_stub_scroll', page_text=Format("{target_page1}\uFE0F\u20E3")),
        Back(Const('⬅️Назад')),
        getter=timetable_view_getter,
        preview_data=timetable_view_getter,
        state=states.Timetable.view_timetable,
    ),
    # Выбираем ученика
    Window(
        Format('Выберете ученика'),
        ScrollingGroup(
            Radio(
                checked_text=Format("🔘 {item[0]}"),
                unchecked_text=Format("️⚪️ {item[0]}"),
                id="radio3_stud",
                item_id_getter=lambda x: x[1],
                items="stud_row",
                # on_click=radio3_click,
                # on_state_changed=radio3_click,
            ),
            width=1,
            height=5,
            id="scroll_with_pager",
        ),
        Row(
            Back(Const('⬅️Назад')),
            Next(Const('Следующий шаг➡️')),
        ),
        state=states.Timetable.add_timetable_step_1,
        getter=get_stud_getter,
    ),
    # Второе окно добавления расписания - выбираем день недели и нужный предмет
    Window(
        Format('Переходим к добавлению нового расписания. '
               'Для начала выберем нужный день недели и предмет (математика/физика), а также введите стоимость занятия'
               'с помощью специального счетчика'),
        Column(
            Radio(
                checked_text=Format('[✅] {item[1]}'),
                unchecked_text=Format('[ ] {item[1]}'),
                id='ch_subject',
                items='subjects',
                item_id_getter=lambda x: x[0],
                checked_style=Style("success"),
                # on_state_changed=selected_subject,
            ),
        ),
        Radio(
            checked_text=Format("✓ {item[1]}"),
            unchecked_text=Format("️ {item[1]}"),
            items="ru_day",
            item_id_getter=lambda x: x[0],
            id="radio2_day_week",
        ),
        Row(
            Back(Const('⬅️Назад')),
            Next(Const('Следующий шаг➡️')),
        ),
        state=states.Timetable.add_timetable_step_2,
        getter=timetable_add_getter
    ),
    # Вводим время занятия
    Window(
        Format('{input_time_text}'),
        TimeSelect(
            id='price_input',
            hour_header=Const('Часы'),
            minute_header=Const('Минуты'),
            on_hour_click=hour_click,
            on_minute_click=minute_click,
        ),
        Row(
            Back(Const('⬅️Назад')),
            Next(Const('Следующий шаг➡️')),
        ),
        state=states.Timetable.add_timetable_step_3,
        getter=input_time_getter,
    ),
    # Окно финальной проверки выбранных/введенных параметров
    Window(
        Format('Заключительный шаг - проверка введенных параметров'),
        Format('{finish_text}'),
        Button(
            Const('Отправить данные'), id='button_clicked', on_click=sending_timetable_data),
        state=states.Timetable.add_timetable_step_4,
        getter=finish_timetable_getter,
    ),
    on_start=set_stud_default,
)

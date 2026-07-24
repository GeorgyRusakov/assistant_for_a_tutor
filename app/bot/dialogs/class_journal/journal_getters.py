from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager, StartMode, Window, ShowMode, ChatEvent
import logging
from app.infrastructure.database.db import get_students, get_subject_stud, get_id_subject_stud, add_class_journal, get_classes_by_year, get_classes_by_month, get_classes_by_month_year
from psycopg import AsyncConnection
from babel.dates import format_date
import calendar
from datetime import datetime
from babel.dates import get_month_names
# from decimal import Decimal

logger = logging.getLogger(__name__)

async def journal_preview_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'window_preview_hello': local['window_preview_hello']}


async def get_stud_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    stud_row = await get_students(conn)
    # print(stud_row)
    lst_stud = [(f'{i[1]}', i[0]) for i in stud_row]
    # pprint(lst_stud)
    dialog_manager.dialog_data.update(stud_row=lst_stud)

    return {'stud_row': lst_stud,
            'len_stud_row': len(stud_row),
            'window_add_lesson_view': local['window_add_lesson_view']}


async def product_getter(**_kwargs):
    months_ru = [calendar.month_name[i] for i in range(1, 13)]
    return {
        "products": [(f"Product {i}", i) for i in range(1, 30)],
        "months_ru": months_ru,
    }


async def selected_student_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    selected_id_stud = dialog_manager.dialog_data.get('selected_stud')
    lst_stud: tuple = dialog_manager.dialog_data.get('stud_row')

    selected_stud = [lst_stud[i][0] for i in range(len(lst_stud)) if lst_stud[i][1] == selected_id_stud]
    subjects = await get_subject_stud(conn, int(selected_id_stud))

    if dialog_manager.dialog_data.get('date') is None:
        current_date = datetime.now()
        formatted_date = format_date(current_date, format='d MMMM', locale='ru')
        dialog_manager.dialog_data.update(date=current_date)
    else:
        current_date = dialog_manager.dialog_data.get('date')
        print(current_date)
        formatted_date = format_date(current_date, format='d MMMM', locale='ru_RU')

    return {'selected_stud': selected_stud[0],
            'subjects': subjects,
            'current_date': formatted_date}


async def get_year_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    try:
        year_row = await get_classes_by_year(conn)

        if not year_row:
            logger.error("Не удалось получить список уникальных лет")
            raise RuntimeError("Ошибка получения списка уникальных лет")

        logger.info(f"Список лет: {year_row}")

        return {'year_row': year_row}

    except Exception as e:
        logger.exception('Ошибка при получении списка годов: %s', e)


async def get_month_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    selected_year = dialog_manager.dialog_data.get('selected_year')

    try:
        month_row = await get_classes_by_month(conn, selected_year)

        if not month_row:
            logger.error("Не удалось получить список месяцев")
            raise RuntimeError("Ошибка получения списка месяцев")

        logger.info(f'Список месяцев: {month_row}')

        months_names = get_month_names(
                "wide", context="stand-alone", locale='ru_RU',
            )

        months_list = [(*i, months_names[int(*i)].capitalize()) for i in month_row]

        logger.info(f'Список Номер - Месяц: {months_list}')

        return {'months_list': months_list}

    except Exception as e:
        logger.exception("Ошибка при получении списка месяцев: %s", e)


async def get_classes_by_month_year_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    selected_month = dialog_manager.dialog_data.get('selected_month')
    selected_year = dialog_manager.dialog_data.get('selected_year')

    try:
        classes_row = await get_classes_by_month_year(conn, selected_month, selected_year)

        if not classes_row:
            logger.error("Не удалось получить список занятий")
            raise RuntimeError("Ошибка получения списка занятий")

        logger.info(f'Список занятий: {classes_row}')

        classes_dict = {record[0]: record[1:] for record in classes_row}
        dialog_manager.dialog_data.update(classes_dict=classes_dict)

        classes_preview = [(i[0], f'{i[5].strftime("%d.%m.%Y")}--{i[1]}--{i[2]}') for i in classes_row]

        return {'classes_dict': classes_preview}

    except Exception as e:
        logger.exception("Ошибка при получении списка занятий: %s", e)


async def view_card_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    selected_id_class_card = dialog_manager.dialog_data.get('selected_id_class_card')
    classes_dict = dialog_manager.dialog_data.get('classes_dict')

    logger.info(f'ID выбранного занятия: {selected_id_class_card}')

    try:
        selected_class_card = classes_dict[selected_id_class_card]

        card_text = (
            f'📋 Карточка занятия \n\n'
            "```"
            '\n'
                f'Имя ученика: {selected_class_card[0]} \n' \
                f'Класс: {selected_class_card[1]} \n' \
                f'Предмет: {selected_class_card[2]} \n' \
                f'Дата проведения: {selected_class_card[4].strftime("%d.%m.%Y")} \n' \
                f'Прайс: {selected_class_card[3]} Руб.'
            "```"
                    )

        return {'view_class_card': card_text}

    except Exception as e:
        logger.error('Ошибка в составлении текста карточки занятия: %s', e)

from aiogram_dialog import DialogManager
from app.infrastructure.database.db import get_students
from ....infrastructure.database.models.students import StudentsData
from psycopg import AsyncConnection
import logging

logger = logging.getLogger(__name__)

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
        ('1-4 класс', '1'),
        ('5 класс', '5'),
        ('6 класс', '6'),
        ('7 класс', '7'),
        ('8 класс', '8'),
        ('9 класс', '9'),
        ('10 класс', '10'),
        ('11 класс', '11'),
    ]

    if dialog_manager.dialog_data.get('lst_grade') is None:
        dialog_manager.dialog_data.update(lst_grade=grade)

    return {'grades': grade,
            'select_grade_sub_price_stud': local['select_grade_sub_price_stud'], }


async def get_text_stud_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'add_del_stud': local['add_del_stud']}


async def window_add_stud_getter(dialog_manager: DialogManager, local: dict, **kwargs):
    return {'window_add_stud': local['window_add_stud']}


async def delete_student_getter(dialog_manager: DialogManager, local: dict, conn: AsyncConnection, **kwargs):
    try:
        students_row = await get_students(conn)

        logger.info('Список студентов: %s', students_row)

        lst_students = [StudentsData(*i) for i in students_row]

        return {'window_del_stud': local['window_del_stud'],
                'lst_students': lst_students}

    except Exception as e:
        logger.exception("Ошибка при получении списка студентов: %s", e)
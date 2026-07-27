import logging
from datetime import datetime, timezone
from typing import Any
# from app.bot.enums.roles import UserRole
from psycopg import AsyncConnection
from datetime import date

logger = logging.getLogger(__name__)


# Функция добавления ученика
async def add_student(
        conn: AsyncConnection,
        *,
        name: str,
        grade: str,
) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                INSERT INTO students(name, grade)
                VALUES(%s, %s)
                ON CONFLICT DO NOTHING
                RETURNING id;
            """,
            params=(name, grade)
        )
        row = await data.fetchone()
        logger.info("Student added")
        return row[0] if row else None


# Функция добавления нового расписания
async def add_timetable(
        conn: AsyncConnection,
        id_student: int,
        id_subject: int,
        day_week: str,
        time: str
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                INSERT INTO timetable(id_student, id_subject, day_week, time)
                VALUES(%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """,
            params=(id_student, id_subject, day_week, time)
        )
    logger.info("Timetable added")


# Функция получения списка учеников
async def get_students(conn: AsyncConnection) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                SELECT id, name, grade FROM students
                WHERE is_deleted = FALSE;
                """
            )
        row = await data.fetchall()
        logger.info("Row is %s", row)
        return row if row else None


# Функция удаления учеников
async def delete_students(conn: AsyncConnection, lst_del_stud: list[int]):
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                UPDATE students
                SET is_deleted = TRUE
                WHERE id = ANY(%s);
                """,
                params=(lst_del_stud,)
            )
        logger.info("Student deleted")


# Функция получения расписания по конкретному дню недели
async def get_timetable(conn: AsyncConnection, day_week) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT stud.name, sub.name, day_week, time FROM timetable AS time
            JOIN students AS stud ON stud.id = time.id_student
            JOIN subject AS sub ON sub.id = time.id_subject
            WHERE day_week = %s
            ORDER BY time ASC;
            """,
            params=(day_week,)
        )
        row = await data.fetchall()
        logger.info("Row is %s", row)
        return row if row else None


# Функция получения последнего добавленного ученика из бд
async def get_context_last_id_stud(conn: AsyncConnection, name_stud, grade_stud) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT id FROM students
            WHERE name = %s and grade = %s
            ORDER BY id DESC
            LIMIT 1;
            """,
            params=(name_stud, grade_stud,)
        )
        row = await data.fetchone()
        logger.info("Row is %s", row)
        return row if row else None


# Функция добавления новых пар (предмет-ученик) в таблицу subject_students
async def add_student_subject(
        conn: AsyncConnection,
        id_subject: int,
        id_student: int,
        price: int,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                INSERT INTO subject_students(id_subject, id_student, price)
                VALUES(%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """,
            params=(id_subject, id_student, price)
        )
    logger.info("Student's subjects have been added")


# Функция получения списка предметов, на которые записан ученик
async def get_subject_stud(conn: AsyncConnection, id_student) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
           SELECT subject.id, subject.name FROM subject
            JOIN subject_students AS sub_stud ON sub_stud.id_subject = subject.id
            Where sub_stud.id_student = %s
            """,
            params=(id_student,)
        )
        row = await data.fetchall()
        logger.info("Row is %s", row)
        return row if row else None


# Функция получения id записи, содержащей, на какой предмет записан ученик
async def get_id_subject_stud(conn: AsyncConnection, id_student, sub_select) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
                   SELECT sub_stud.id FROM subject_students AS sub_stud
                    Where sub_stud.id_student = %s AND sub_stud.id_subject = %s
                    """,
            params=(id_student, sub_select)
        )
        row = await data.fetchone()
        logger.info("Row is %s", row)
        return row if row else None


# Функция добавления новой записи в журнал занятий
async def add_class_journal(
        conn: AsyncConnection,
        id_subject_student: int,
        select_day: date,
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                INSERT INTO class_journal(id_subject_students, date)
                VALUES(%s, %s)
                ON CONFLICT DO NOTHING;
            """,
            params=(id_subject_student, select_day,)
        )
    logger.info("Запись успешно добавлена")


async def get_sum_price_week(conn: AsyncConnection, start_week, end_week) -> tuple[Any, ...] | None:
    """Получает суммарную стоимость занятий за неделю"""
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT SUM(sub_stud.price) FROM subject_students AS sub_stud
            JOIN class_journal AS cls ON cls.id_subject_students = sub_stud.id
            WHERE cls.date >= %s::date AND cls.date <= %s::date
            """,
            params=(start_week, end_week,)
        )
        row = await data.fetchone()
        logger.info("Row is %s", row)
        return row if row else None


# Функция получения суммарной стоимости занятий за месяц
async def get_sum_price_month(conn: AsyncConnection, current_month) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT SUM(sub_stud.price) FROM subject_students AS sub_stud
            JOIN class_journal AS cls ON cls.id_subject_students = sub_stud.id
            WHERE EXTRACT(MONTH FROM cls.date) = %s;
            """,
            params=(current_month,)
        )
        row = await data.fetchone()
        logger.info("Row is %s", row)
        return row if row else None


async def get_statistics_for_the_week(conn: AsyncConnection, start_week, end_week) -> tuple[Any, ...] | None:
    """Получает статистику за неделю по каждому ученику"""
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT s.name, COUNT(*) AS number_classes, SUM(ss.price) AS total_income
            FROM class_journal cj
            JOIN subject_students ss ON cj.id_subject_students = ss.id
            JOIN students s ON ss.id_student = s.id
            WHERE cj.date BETWEEN %s::date AND %s::date
            GROUP BY s.name
            ORDER BY total_income DESC;
            """,
            params=(start_week, end_week,)
        )
        row = await data.fetchall()
        logger.info("Row is %s", row)
        return row if row else None


# Функция получения списка уникальных годов
async def get_classes_by_year(conn: AsyncConnection) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT EXTRACT(YEAR FROM cl.date) as year FROM class_journal cl
            GROUP BY year;
            """
        )
        row = await data.fetchall()
        logger.info("Row is %s", row)
        return row if row else None

# Функция получения списка уникальных месяцев
async def get_classes_by_month(conn: AsyncConnection, year: int) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT EXTRACT(MONTH FROM cl.date) as month FROM class_journal cl
            WHERE EXTRACT(YEAR FROM cl.date) = %s
            GROUP BY month;
            """,
            params=(year,)
        )
        row = await data.fetchall()
        logger.info("Row is %s", row)
        return row if row else None


# Функция получения списка занятий за выбранный период (месяц - год)
async def get_classes_by_month_year(conn: AsyncConnection, month: int, year: int) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT cls.id, stud.name, stud.grade, sub.name, sub_stud.price, cls.date FROM students as stud
            JOIN subject_students as sub_stud ON sub_stud.id_student = stud.id
            JOIN class_journal as cls ON cls.id_subject_students = sub_stud.id
			JOIN subject as sub ON sub.id = sub_stud.id_subject
			WHERE EXTRACT(YEAR FROM date) = %s and EXTRACT(MONTH FROM date) = %s
            ORDER BY date DESC;
            """,
            params=(year, month,)
        )
        row = await data.fetchall()
        logger.info("Row is %s", row)
        return row if row else None


# Функция получения всех проведенных занятий (сохраняю на всякий случай)
async def get_completed_lesson(conn: AsyncConnection, current_month) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
            SELECT stud.name, stud.grade, sub_stud.price, cls.date FROM students as stud
            JOIN subject_students as sub_stud ON sub_stud.id_student = stud.id
            JOIN class_journal as cls ON cls.id_subject_students = sub_stud.id
            ORDER BY date DESC
            """,
            params=(current_month,)
        )
        row = await data.fetchone()
        logger.info("Row is %s", row)
        return row if row else None


# Функция для получения статистики суммы занятий по месяцам
async def get_sum_months(conn: AsyncConnection, current_month) -> tuple[Any, ...] | None:
    async with conn.cursor() as cursor:
        data = await cursor.execute(
            query="""
               SELECT EXTRACT(MONTH FROM cls.date) as month, SUM(sub_stud.price) FROM subject_students AS sub_stud
               JOIN class_journal AS cls ON cls.id_subject_students = sub_stud.id
               GROUP BY month
               """,
            params=(current_month,)
        )
        row = await data.fetchone()
        logger.info("Row is %s", row)
        return row if row else None

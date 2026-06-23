import asyncio
import logging
import os
import sys

from app.infrastructure.database.connection import get_pg_connection
from config.config import Config, load_config
from psycopg import AsyncConnection, Error

config: Config = load_config()

logging.basicConfig(
    level=logging.getLevelName(level=config.log.level),
    format=config.log.format,
)

logger = logging.getLogger(__name__)

if sys.platform.startswith("win") or os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    connection: AsyncConnection | None = None

    try:
        connection = await get_pg_connection(
            db_name=config.db.name,
            host=config.db.host,
            port=config.db.port,
            user=config.db.user,
            password=config.db.password,
        )
        async with connection:
            async with connection.transaction():
                async with connection.cursor() as cursor:
                    await cursor.execute(
                        query="""
                        INSERT INTO students (name, grade) VALUES
                            ('Илья Мещеряков', '11 класс'),
                            ('Иван Байдиков', '11 класс'),
                            ('Глеб Соколов', '8 класс'),
                            ('Василиса Орлова', '5 класс'),
                            ('Артём Петров', '7 класс'),
                            ('Мария Кузнецова', '9 класс'),
                            ('Дарья Волкова', '10 класс');
                        """
                    )
                    await cursor.execute(
                        query="""
                        INSERT INTO subject (name) VALUES
                            ('математика'),
                            ('физика'),
                            ('информатика'),
                            ('химия'),
                            ('английский язык'),
                            ('русский язык'),
                            ('биология');
                        """
                    )
                    await cursor.execute(
                        query="""
                        INSERT INTO subject_students (id_subject, id_student, price) VALUES
                            (1, 1, 1200),
                            (1, 2, 1100),
                            (2, 3, 1000),
                            (1, 4, 1000),
                            (3, 5, 1500),
                            (2, 6, 1300),
                            (5, 7, 1400);
                        """
                    )
                    await cursor.execute(
                        query="""
                        INSERT INTO class_journal (id_subject_students, date) VALUES
                            (1, '2026-03-01'),
                            (2, '2026-03-01'),
                            (3, '2026-03-02'),
                            (3, '2026-03-04'),
                            (5, '2026-03-04'),
                            (2, '2026-03-06'),
                            (4, '2026-03-07');
                        """
                    )
                    await cursor.execute(
                        query="""
                        INSERT INTO timetable (id_student, id_subject, day_week, time) VALUES
                            (1, 1, 'четверг', '16:30:00'),
                            (2, 1, 'пятница', '17:00:00'),
                            (3, 2, 'понедельник', '10:00:00'),
                            (4, 1, 'воскресенье', '10:45:00'),
                            (5, 3, 'среда', '17:30:00'),
                            (6, 2, 'понедельник', '18:00:00'),
                            (7, 5, 'суббота', '15:00:00');
                        """
                    )
                logger.info("Tables were successfully filled with data")
    except Error as db_error:
        logger.exception("Database-specific error: %s", db_error)
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        if connection:
            await connection.close()
            logger.info("Connection to Postgres closed")


asyncio.run(main())
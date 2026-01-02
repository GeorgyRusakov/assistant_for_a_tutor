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
                            CREATE TABLE IF NOT EXISTS students(
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(30) NOT NULL,
                            grade VARCHAR(10) NOT NULL
                            );
                            """
                    )
                    await cursor.execute(
                        query="""
                        CREATE TABLE IF NOT EXISTS subject(
                        id SERIAL PRIMARY KEY,
                        item_name VARCHAR(20) NOT NULL
                        );
                        """
                    )
                    await cursor.execute(
                        query="""
                        CREATE TABLE IF NOT EXISTS classes
                        id SERIAL PRIMARY KEY,
                        id_student INT NOT NULL REFERENCES students(id),
                        id_subject INT NOT NULL REFERENCES subject(id),
                        class_date DATE NOT NULL DEFAULT CURRENT_DATE,
                        price INT NOT NULL REFERENCES timetable(price)
                        );
                        """
                    )
                    await cursor.execute(
                        query="""
                        CREATE TABLE IF NOT EXISTS timetable
                        id SERIAL PRIMARY KEY,
                        id_student INT NOT NULL REFERENCES students(id),
                        id_subject INT NOT NULL REFERENCES subject(id),
                        day_week VARCHAR(20) NOT NULL,
                        time TIMESTAMPTZ NOT NULL,
                        price INT NOT NUll
                        );
                        """
                    )
                logger.info("Tables `students`, `subject`, classes`, `timetable` were successfully created")
    except Error as db_error:
        logger.exception("Database-specific error: %s", db_error)
    except Exception as e:
        logger.exception("Unhandled error: %s", e)
    finally:
        if connection:
            await connection.close()
            logger.info("Connection to Postgres closed")


asyncio.run(main())

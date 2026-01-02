import logging
from datetime import datetime, timezone
from typing import Any
# from app.bot.enums.roles import UserRole
from psycopg import AsyncConnection

logger = logging.getLogger(__name__)


async def add_student(
        conn: AsyncConnection,
        *,
        name: str,
        grade: str,
        price: int,
        subject: str
) -> None:
    async with conn.cursor() as cursor:
        await cursor.execute(
            query="""
                INSERT INTO students(name, grade, price, subject)
                VALUES(%s, %s, %s, %s) 
                ON CONFLICT DO NOTHING;
            """,
            params=(name, grade, price, subject)
        )
    logger.info("Student added")

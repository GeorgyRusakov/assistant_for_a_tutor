import asyncio
import logging

from config.config import Config, load_config
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.bot.handlers.handlers import user_router, start_dialog
from aiogram_dialog import setup_dialogs
from app.locale.ru import RU
from app.bot.middelwares.db_middleware import DataBaseMiddleware
from app.infrastructure.database.connection import get_pg_pool
import psycopg_pool
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


async def main() -> None:
    config: Config = load_config()

    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )

    logger.info('Starting bot')

    storage = RedisStorage(
        redis=Redis(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
            password=config.redis.password,
            username=config.redis.username,
        )
    )

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.name,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
    )
    logger.info("Including routers...")
    dp.include_routers(user_router)
    dp.include_routers(start_dialog)
    setup_dialogs(dp)

    logger.info("Including middlewares...")
    dp.update.middleware(DataBaseMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot, local=RU,
                               db_pool=db_pool)
    except Exception as e:
        logger.exception(e)
    finally:
        await db_pool.close()
        logger.info("Connection to Postgres closed")


asyncio.run(main())

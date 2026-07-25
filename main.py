import asyncio
import sys
import logging

from config.config import Config, load_config
from aiogram import Bot, Dispatcher
# from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


from app.bot.dialogs.start_dlg import start_dialog, user_router
from app.bot.dialogs.menu_dlg import main_menu
# from app.bot.dialogs.add_delete_stud import add_del_stud
# from app.bot.dialogs.class_journal_exp import class_journal
from app.bot.dialogs.crud_student.crud_stud_dialogs import crud_student
from app.bot.dialogs.class_journal.journal_dialogs import journal_dialogs
from app.bot.dialogs.financial_statements.dialogs.fin_dialogs import finance
from app.bot.dialogs.timetable.timetable_dialogs import timetable_dlg
# from app.bot.dialogs.timetable_dlg import timetable_dlg


from aiogram_dialog import setup_dialogs
from app.locale.ru import RU
from app.bot.middelwares.db_middleware import DataBaseMiddleware
# from app.bot.middelwares.text_middleware import GetTextMiddleware
from app.infrastructure.database.connection import get_pg_pool
import psycopg_pool
# from redis.asyncio import Redis
from aiogram.client.session.aiohttp import AiohttpSession
from aiohttp_socks import ProxyConnector
from aiohttp import ClientSession

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = logging.getLogger(__name__)


async def main() -> None:
    config: Config = load_config()

    proxy_url = f'socks5://{config.proxy.login}:{config.proxy.password}@{config.proxy.ip}:{config.proxy.port}'
    # connector = ProxyConnector.from_url(proxy_url)
    session = AiohttpSession(
        proxy=proxy_url  # Для aiogram 3.x это самый короткий путь
    )

    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
    )

    logger.info('Starting bot')

    # storage = RedisStorage(
    #     redis=Redis(
    #         host=config.redis.host,
    #         port=config.redis.port,
    #         db=config.redis.db,
    #         password=config.redis.password,
    #         username=config.redis.username,
    #     )
    # )

    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=session
    )
    # dp = Dispatcher(storage=storage)
    dp = Dispatcher()

    db_pool: psycopg_pool.AsyncConnectionPool = await get_pg_pool(
        db_name=config.db.name,
        host=config.db.host,
        port=config.db.port,
        user=config.db.user,
        password=config.db.password,
    )
    logger.info("Including routers and dialogs...")
    dp.include_routers(user_router)
    dp.include_routers(start_dialog)
    dp.include_routers(main_menu)
    dp.include_routers(crud_student)
    # dp.include_routers(class_journal)
    dp.include_routers(journal_dialogs)
    dp.include_routers(timetable_dlg)
    dp.include_routers(finance)
    setup_dialogs(dp)

    logger.info("Including middlewares...")
    dp.update.middleware(DataBaseMiddleware())
    # dp.update.middleware(GetTextMiddleware())

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

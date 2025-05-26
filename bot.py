"""
Основной модуль Telegram бота для управления корпоративными сборами и уведомлениями.

Этот модуль инициализирует бота, настраивает обработчики команд, middleware и планировщик задач.
Он также отвечает за настройку логирования и обработку основных исключений.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from database import init_db
from utils.middleware import AntiSpamMiddleware, LoggingMiddleware
from handlers import (
    user,
    admin,
    registration,
    fund_management,
    broadcasts
)
from scheduler import NotificationScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main() -> None:
    """
    Основная асинхронная функция для запуска бота.
    
    Выполняет следующие действия:
    1. Инициализирует базу данных
    2. Создает экземпляр бота и диспетчера
    3. Регистрирует middleware и обработчики команд
    4. Запускает планировщик задач
    5. Запускает поллинг бота
    
    Raises:
        Exception: При возникновении непредвиденных ошибок в работе бота
    """
    # Инициализация базы данных
    init_db()
    
    # Создаем сессию с настроенным HTTP-клиентом
    session = AiohttpSession()
    
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация middleware
    dp.update.outer_middleware(AntiSpamMiddleware())
    dp.update.outer_middleware(LoggingMiddleware())
    
    # Регистрация хендлеров
    dp.include_router(registration.router)
    dp.include_router(user.router)
    dp.include_router(fund_management.router)
    dp.include_router(admin.router)
    dp.include_router(broadcasts.router)
    
    # Инициализация и запуск планировщика
    scheduler = NotificationScheduler()
    scheduler.start()
    
    try:
        # Удаление вебхука на всякий случай
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Запуск поллинга
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        # Остановка планировщика при завершении
        scheduler.shutdown()
        await session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

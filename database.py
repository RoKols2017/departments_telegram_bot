# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from models.base import Base
import logging
from alembic.config import Config
from alembic import command
from pathlib import Path

# Настройка логгера
logger = logging.getLogger(__name__)

# Асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Фабрика асинхронных сессий
async_session_factory = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Экспортируем для использования в сервисах
__all__ = ["engine", "async_session_factory", "Base"]

# Функции инициализации и Alembic оставлены для ручного вызова или переписывания отдельно при необходимости


def init_db():
    """
    Инициализация базы данных:
    - Создание всех таблиц
    - Применение миграций
    """
    try:
        # Создание директории для миграций, если её нет
        migrations_dir = Path("migrations")
        migrations_dir.mkdir(exist_ok=True)

        # Настройка Alembic
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", str(migrations_dir))
        alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)

        # Создание таблиц
        await Base.metadata.create_all(bind=engine)

        # Применение миграций
        await command.upgrade(alembic_cfg, "head")

        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def get_engine():
    """
    Получение текущего движка базы данных
    """
    return engine

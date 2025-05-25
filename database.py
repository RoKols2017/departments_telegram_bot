# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from config import DATABASE_URL
import logging
from alembic.config import Config
from alembic import command
from pathlib import Path

# Настройка логгера
logger = logging.getLogger(__name__)

# Создание движка базы данных
engine = create_engine(DATABASE_URL, echo=True)

# Создание фабрики сессий
session_factory = sessionmaker(bind=engine)
SessionLocal = scoped_session(session_factory)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """
    Генератор для получения сессии базы данных.
    Гарантирует закрытие сессии после использования.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
        Base.metadata.create_all(bind=engine)
        
        # Применение миграций
        command.upgrade(alembic_cfg, "head")
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def get_engine():
    """
    Получение текущего движка базы данных
    """
    return engine

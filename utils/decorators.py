# utils/decorators.py

from functools import wraps
from aiogram import types
from database import SessionLocal, async_session_factory
from models import User, Log
from datetime import datetime


def role_required(roles: list[str]):
    """
    Проверка ролей пользователя
    """

    def decorator(handler):
        @wraps(handler)
        async def wrapper(message: types.Message, session, *args, **kwargs):
            user = (
                session.query(User).filter_by(telegram_id=message.from_user.id).first()
            )
            if not user:
                await message.answer("❌ Вы не зарегистрированы.")
                return

            if user.role not in roles:
                await message.answer("⛔ Нет доступа к этой команде.")
                return

            return await handler(message, session, user, *args, **kwargs)

        return wrapper

    return decorator


def ensure_registered():
    """
    Проверка регистрации. Ожидает, что session уже передан как второй аргумент.
    """

    def decorator(handler):
        @wraps(handler)
        async def wrapper(message, session, *args, **kwargs):
            user = (
                session.query(User).filter_by(telegram_id=message.from_user.id).first()
            )
            if not user:
                await message.answer(
                    "❌ Вы не зарегистрированы. Введите /start для регистрации."
                )
                return
            return await handler(message, session, user, *args, **kwargs)

        return wrapper

    return decorator


def log_action(action_name: str):
    """
    Логирование действий пользователя
    """

    def decorator(handler):
        @wraps(handler)
        async def wrapper(message: types.Message, session, *args, **kwargs):
            session.add(
                Log(
                    user_id=message.from_user.id,
                    action=action_name,
                    timestamp=datetime.utcnow(),
                )
            )
            session.commit()
            return await handler(message, session, *args, **kwargs)

        return wrapper

    return decorator


def with_db_session_async(handler):
    """
    Асинхронный декоратор для автоматического создания и закрытия сессии БД в aiogram-обработчиках.
    Передаёт session как второй аргумент в handler.
    """

    @wraps(handler)
    async def wrapper(message, *args, **kwargs):
        async with async_session_factory() as session:
            async with session.begin():
                return await handler(message, session, *args, **kwargs)

    return wrapper

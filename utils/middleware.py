from typing import Dict, Callable, Any, Awaitable
from datetime import datetime, timedelta
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
import logging
import sqlite3
from collections import defaultdict


class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: int = 5):
        self.rate_limit = rate_limit  # Количество сообщений
        self.user_messages: Dict[int, list] = defaultdict(list)
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id
        current_time = datetime.now()

        # Очистка старых сообщений (старше 1 минуты)
        self.user_messages[user_id] = [
            msg_time
            for msg_time in self.user_messages[user_id]
            if current_time - msg_time < timedelta(minutes=1)
        ]

        # Добавление текущего сообщения
        self.user_messages[user_id].append(current_time)

        # Проверка на спам
        if len(self.user_messages[user_id]) > self.rate_limit:
            await event.answer(
                "Пожалуйста, подождите минуту перед следующим сообщением."
            )
            return None

        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, db_path: str = "data/logs.db"):
        self.db_path = db_path
        self._init_db()
        super().__init__()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id INTEGER,
                username TEXT,
                command TEXT,
                message_text TEXT,
                role TEXT
            )
        """
        )
        conn.commit()
        conn.close()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        # Логируем входящее сообщение
        user_id = event.from_user.id
        username = event.from_user.username
        command = event.get_command()
        message_text = event.text

        # Получаем роль пользователя из контекста (если есть)
        role = data.get("role", "unknown")

        # Записываем в БД
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO bot_logs (user_id, username, command, message_text, role) VALUES (?, ?, ?, ?, ?)",
            (user_id, username, command, message_text, role),
        )
        conn.commit()
        conn.close()

        return await handler(event, data)

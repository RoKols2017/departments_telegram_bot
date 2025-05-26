"""
Вспомогательные функции для работы с датами, сотрудниками и логированием действий.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from models import Staff, Log
from typing import List

def get_birthday_staff_ids(session: Session, month_list: List[int]) -> List[int]:
    """
    Возвращает список ID сотрудников, у которых день рождения в указанных месяцах.

    Args:
        session (Session): SQLAlchemy-сессия.
        month_list (List[int]): Список номеров месяцев.

    Returns:
        List[int]: Список ID сотрудников.
    """
    return [s.id for s in session.query(Staff).all() if s.birthday and s.birthday.month in month_list]

def format_date(date: datetime) -> str:
    """
    Форматирует дату в строку вида 'ДД.ММ.ГГГГ'.

    Args:
        date (datetime): Дата для форматирования.

    Returns:
        str: Отформатированная дата.
    """
    return date.strftime('%d.%m.%Y')

def safe_log(session: Session, user_id: int, action: str) -> None:
    """
    Сохраняет действие пользователя в лог.

    Args:
        session (Session): SQLAlchemy-сессия.
        user_id (int): ID пользователя.
        action (str): Описание действия.
    """
    session.add(Log(user_id=user_id, action=action, timestamp=datetime.utcnow()))
    session.commit()

def is_admin(role: str) -> bool:
    """
    Проверяет, является ли роль административной.

    Args:
        role (str): Название роли.

    Returns:
        bool: True, если роль admin или superadmin.
    """
    return role in ["admin", "superadmin"]

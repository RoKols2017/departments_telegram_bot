# services/birthday_service.py
from datetime import datetime, timedelta
from sqlalchemy import select
from models import Staff
from config import BIRTHDAY_REMINDER_DAYS_BEFORE

"""
Сервис для работы с днями рождения: поиск ближайших дней рождения сотрудников.
"""


async def get_upcoming_birthdays(session):
    """
    Возвращает список сотрудников, у которых день рождения через заданное число дней (BIRTHDAY_REMINDER_DAYS_BEFORE).
    """
    today = datetime.today().date()
    target_date = today + timedelta(days=BIRTHDAY_REMINDER_DAYS_BEFORE)
    result = await session.execute(
        select(Staff).where(
            Staff.birthday.isnot(None),
            Staff.birthday.month == target_date.month,
            Staff.birthday.day == target_date.day
        )
    )
    return result.scalars().all()

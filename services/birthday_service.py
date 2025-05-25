# services/birthday_service.py
from datetime import datetime, timedelta
from database import SessionLocal
from models import Staff, User
from config import BIRTHDAY_REMINDER_DAYS_BEFORE

def get_upcoming_birthdays():
    session = SessionLocal()
    try:
        today = datetime.today().date()
        target_date = today + timedelta(days=BIRTHDAY_REMINDER_DAYS_BEFORE)
        return session.query(Staff).filter(
            Staff.birthday != None,
            Staff.birthday.month == target_date.month,
            Staff.birthday.day == target_date.day
        ).all()
    finally:
        session.close()

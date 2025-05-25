from datetime import datetime
from models import Staff, Log
from database import SessionLocal

def get_birthday_staff_ids(session, month_list):
    return [s.id for s in session.query(Staff).all() if s.birthday and s.birthday.month in month_list]

def format_date(date: datetime):
    return date.strftime('%d.%m.%Y')

def safe_log(session, user_id, action):
    session.add(Log(user_id=user_id, action=action, timestamp=datetime.utcnow()))
    session.commit()

def is_admin(role: str) -> bool:
    return role in ["admin", "superadmin"]

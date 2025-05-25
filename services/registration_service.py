# services/registration_service.py
from database import SessionLocal
from models import User, Staff

def is_registered(telegram_id: int) -> bool:
    session = SessionLocal()
    try:
        return session.query(User).filter_by(telegram_id=telegram_id).first() is not None
    finally:
        session.close()

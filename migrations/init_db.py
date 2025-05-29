from sqlalchemy.orm import Session
from models import Role, User
from config import SUPERADMIN_ID
import logging

logger = logging.getLogger(__name__)


def init_roles(db: Session):
    """Инициализация базовых ролей"""
    default_roles = [
        {"name": "user", "description": "Обычный пользователь"},
        {"name": "treasurer", "description": "Казначей сборов"},
        {"name": "admin", "description": "Администратор"},
        {"name": "superadmin", "description": "Суперадминистратор"},
    ]

    try:
        for role_data in default_roles:
            role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not role:
                role = Role(**role_data)
                db.add(role)
                logger.info(f"Created role: {role_data['name']}")

        db.commit()
    except Exception as e:
        logger.error(f"Error creating roles: {e}")
        db.rollback()
        raise


def init_superadmin(db: Session):
    """Инициализация суперадминистратора"""
    try:
        # Проверяем существование суперадмина
        superadmin = db.query(User).filter(User.telegram_id == SUPERADMIN_ID).first()
        if not superadmin:
            # Создаем пользователя-суперадмина
            superadmin = User(
                telegram_id=SUPERADMIN_ID, employee_id="SUPERADMIN", is_active=True
            )
            db.add(superadmin)
            db.commit()
            db.refresh(superadmin)

            # Назначаем роль суперадмина
            superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
            if superadmin_role:
                superadmin.roles.append(superadmin_role)
                db.commit()
                logger.info(f"Created superadmin user with ID: {SUPERADMIN_ID}")
    except Exception as e:
        logger.error(f"Error creating superadmin: {e}")
        db.rollback()
        raise


def init_database(db: Session):
    """Инициализация базы данных"""
    try:
        # Создаем роли
        init_roles(db)

        # Создаем суперадмина
        init_superadmin(db)

        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

"""
Сервис для управления пользователями: создание, обновление, роли, поиск.
"""
# services/user_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import User, Role, UserRole
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class UserService:
    """
    Сервис для работы с пользователями (создание, поиск, управление ролями и статусом).
    Использует SQLAlchemy-сессию для всех операций с БД.
    """
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, telegram_id: int, employee_id: str, **kwargs) -> User:
        """Создание нового пользователя"""
        try:
            user = User(
                telegram_id=telegram_id,
                employee_id=employee_id,
                **kwargs
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            self.db.rollback()
            raise

    def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по Telegram ID"""
        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def get_user_by_employee_id(self, employee_id: str) -> Optional[User]:
        """Получение пользователя по табельному номеру"""
        return self.db.query(User).filter(User.employee_id == employee_id).first()

    def get_all_active_users(self) -> List[User]:
        """Получение всех активных пользователей"""
        return self.db.query(User).filter(User.is_active == True).all()

    def get_users_by_role(self, role_name: str) -> List[User]:
        """Получение пользователей по роли"""
        return self.db.query(User).join(User.roles).filter(Role.name == role_name).all()

    def add_role_to_user(self, user_id: int, role_name: str) -> bool:
        """Добавление роли пользователю"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            role = self.db.query(Role).filter(Role.name == role_name).first()
            
            if user and role and role not in user.roles:
                user.roles.append(role)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding role to user: {e}")
            self.db.rollback()
            return False

    def remove_role_from_user(self, user_id: int, role_name: str) -> bool:
        """Удаление роли у пользователя"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            role = self.db.query(Role).filter(Role.name == role_name).first()
            
            if user and role and role in user.roles:
                user.roles.remove(role)
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing role from user: {e}")
            self.db.rollback()
            return False

    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Обновление данных пользователя"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                self.db.commit()
                self.db.refresh(user)
                return user
            return None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            self.db.rollback()
            return None

    def deactivate_user(self, user_id: int) -> bool:
        """Деактивация пользователя"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_active = False
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            self.db.rollback()
            return False

    def get_user_roles(self, user_id: int) -> List[str]:
        """Получение списка ролей пользователя"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return [role.name for role in user.roles]
        return []

    def has_role(self, user_id: int, role_name: str) -> bool:
        """Проверка наличия роли у пользователя"""
        return role_name in self.get_user_roles(user_id)

    def get_admins(self) -> List[User]:
        """Получение списка администраторов"""
        return self.get_users_by_role('admin')

    def get_superadmins(self) -> List[User]:
        """Получение списка суперадминистраторов"""
        return self.get_users_by_role('superadmin')

    def get_treasurers(self) -> List[User]:
        """Получение списка казначеев"""
        return self.get_users_by_role('treasurer')

"""
Сервис для управления пользователями: создание, обновление, роли, поиск.
"""

# services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User, Role
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class UserService:
    """
    Асинхронный сервис для работы с пользователями (создание, поиск, управление ролями и статусом).
    Использует AsyncSession для всех операций с БД.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, telegram_id: int, employee_id: str, **kwargs) -> User:
        """Создание нового пользователя"""
        try:
            user = User(telegram_id=telegram_id, employee_id=employee_id, **kwargs)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            await self.db.rollback()
            raise

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по Telegram ID"""
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def get_user_by_employee_id(self, employee_id: str) -> Optional[User]:
        """Получение пользователя по табельному номеру"""
        result = await self.db.execute(
            select(User).where(User.employee_id == employee_id)
        )
        return result.scalar_one_or_none()

    async def get_all_active_users(self) -> List[User]:
        """Получение всех активных пользователей"""
        result = await self.db.execute(select(User).where(User.is_active.is_(True)))
        return result.scalars().all()

    async def get_users_by_role(self, role_name: str) -> List[User]:
        """Получение пользователей по роли"""
        result = await self.db.execute(
            select(User).join(User.roles).where(Role.name == role_name)
        )
        return result.scalars().all()

    async def add_role_to_user(self, user_id: int, role_name: str) -> bool:
        """Добавление роли пользователю"""
        try:
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            role_result = await self.db.execute(
                select(Role).where(Role.name == role_name)
            )
            role = role_result.scalar_one_or_none()

            if user and role and role not in user.roles:
                user.roles.append(role)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding role to user: {e}")
            await self.db.rollback()
            return False

    async def remove_role_from_user(self, user_id: int, role_name: str) -> bool:
        """Удаление роли у пользователя"""
        try:
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            role_result = await self.db.execute(
                select(Role).where(Role.name == role_name)
            )
            role = role_result.scalar_one_or_none()

            if user and role and role in user.roles:
                user.roles.remove(role)
                await self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing role from user: {e}")
            await self.db.rollback()
            return False

    async def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Обновление данных пользователя"""
        try:
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                await self.db.commit()
                await self.db.refresh(user)
                return user
            return None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            await self.db.rollback()
            return None

    async def deactivate_user(self, user_id: int) -> bool:
        """Деактивация пользователя"""
        try:
            user_result = await self.db.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user.is_active = False
                await self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            await self.db.rollback()
            return False

    async def get_user_roles(self, user_id: int) -> List[str]:
        """Получение списка ролей пользователя"""
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if user:
            return [role.name for role in user.roles]
        return []

    async def has_role(self, user_id: int, role_name: str) -> bool:
        """Проверка наличия роли у пользователя"""
        return role_name in await self.get_user_roles(user_id)

    async def get_admins(self) -> List[User]:
        """Получение списка администраторов"""
        return await self.get_users_by_role("admin")

    async def get_superadmins(self) -> List[User]:
        """Получение списка суперадминистраторов"""
        return await self.get_users_by_role("superadmin")

    async def get_treasurers(self) -> List[User]:
        """Получение списка казначеев"""
        return await self.get_users_by_role("treasurer")

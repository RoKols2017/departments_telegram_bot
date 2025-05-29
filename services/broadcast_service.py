"""
Сервис для управления рассылками и уведомлениями: создание, отправка, статус.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from models import User, Broadcast, Notification
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class BroadcastService:
    """
    Сервис для работы с рассылками и уведомлениями (создание, отправка, статус).
    Использует SQLAlchemy-сессию для всех операций с БД.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_broadcast(
        self,
        sender_id: int,
        title: str,
        message: str,
        broadcast_type: str,
        target_department: Optional[str] = None,
        scheduled_for: Optional[datetime] = None,
    ) -> Broadcast:
        """Создание новой рассылки"""
        try:
            broadcast = Broadcast(
                sender_id=sender_id,
                title=title,
                message=message,
                broadcast_type=broadcast_type,
                target_department=target_department,
                scheduled_for=scheduled_for,
            )
            self.db.add(broadcast)
            await self.db.commit()
            await self.db.refresh(broadcast)
            return broadcast
        except Exception as e:
            logger.error(f"Error creating broadcast: {e}")
            await self.db.rollback()
            raise

    async def get_broadcast(self, broadcast_id: int) -> Optional[Broadcast]:
        """Получение рассылки по ID"""
        result = await self.db.execute(
            select(Broadcast).where(Broadcast.id == broadcast_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_broadcasts(self) -> List[Broadcast]:
        """Получение всех ожидающих отправки рассылок"""
        now = datetime.now()
        result = await self.db.execute(
            select(Broadcast).where(
                and_(
                    Broadcast.scheduled_for <= now, Broadcast.scheduled_for.isnot(None)
                )
            )
        )
        return result.scalars().all()

    async def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str,
        scheduled_for: Optional[datetime] = None,
    ) -> Notification:
        """Создание нового уведомления"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                scheduled_for=scheduled_for,
                is_read=False,
            )
            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            await self.db.rollback()
            raise

    async def get_user_notifications(
        self, user_id: int, unread_only: bool = False
    ) -> List[Notification]:
        """Получение уведомлений пользователя"""
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        result = await self.db.execute(stmt.order_by(Notification.created_at.desc()))
        return result.scalars().all()

    async def mark_notification_as_read(self, notification_id: int) -> bool:
        """Отметка уведомления как прочитанного"""
        try:
            result = await self.db.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            if notification:
                notification.is_read = True
                await self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            await self.db.rollback()
            return False

    async def send_broadcast_to_users(self, broadcast: Broadcast) -> List[Notification]:
        """Отправка рассылки пользователям"""
        try:
            notifications = []
            users_query = select(User).where(User.is_active.is_(True))

            # Фильтрация пользователей в зависимости от типа рассылки
            if broadcast.broadcast_type == "department" and broadcast.target_department:
                users_query = users_query.where(
                    User.department == broadcast.target_department
                )
            elif broadcast.broadcast_type == "no_birthday":
                today = datetime.now()
                users_query = users_query.where(
                    or_(User.birthday.is_(None), User.birthday != today)
                )

            result = await self.db.execute(users_query)
            users = result.scalars().all()

            # Создание уведомлений для каждого пользователя
            for user in users:
                notification = await self.create_notification(
                    user_id=user.id,
                    title=broadcast.title,
                    message=broadcast.message,
                    notification_type="broadcast",
                )
                notifications.append(notification)

            return notifications
        except Exception as e:
            logger.error(f"Error sending broadcast: {e}")
            await self.db.rollback()
            return []

    async def delete_old_notifications(self, days: int = 30) -> int:
        """Удаление старых уведомлений"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            result = await self.db.execute(
                select(Notification).where(Notification.created_at < cutoff_date)
            )
            notifications = result.scalars().all()
            for notification in notifications:
                await self.db.delete(notification)
            await self.db.commit()
            return len(notifications)
        except Exception as e:
            logger.error(f"Error deleting old notifications: {e}")
            await self.db.rollback()
            return 0

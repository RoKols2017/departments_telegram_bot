"""
Сервис для управления рассылками и уведомлениями: создание, отправка, статус.
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
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
    def __init__(self, db: Session):
        self.db = db

    def create_broadcast(
        self,
        sender_id: int,
        title: str,
        message: str,
        broadcast_type: str,
        target_department: Optional[str] = None,
        scheduled_for: Optional[datetime] = None
    ) -> Broadcast:
        """Создание новой рассылки"""
        try:
            broadcast = Broadcast(
                sender_id=sender_id,
                title=title,
                message=message,
                broadcast_type=broadcast_type,
                target_department=target_department,
                scheduled_for=scheduled_for
            )
            self.db.add(broadcast)
            self.db.commit()
            self.db.refresh(broadcast)
            return broadcast
        except Exception as e:
            logger.error(f"Error creating broadcast: {e}")
            self.db.rollback()
            raise

    def get_broadcast(self, broadcast_id: int) -> Optional[Broadcast]:
        """Получение рассылки по ID"""
        return self.db.query(Broadcast).filter(Broadcast.id == broadcast_id).first()

    def get_pending_broadcasts(self) -> List[Broadcast]:
        """Получение всех ожидающих отправки рассылок"""
        now = datetime.now()
        return self.db.query(Broadcast).filter(
            and_(
                Broadcast.scheduled_for <= now,
                Broadcast.scheduled_for.isnot(None)
            )
        ).all()

    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: str,
        scheduled_for: Optional[datetime] = None
    ) -> Notification:
        """Создание нового уведомления"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                type=notification_type,
                scheduled_for=scheduled_for,
                is_read=False
            )
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            return notification
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            self.db.rollback()
            raise

    def get_user_notifications(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        """Получение уведомлений пользователя"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).all()

    def mark_notification_as_read(self, notification_id: int) -> bool:
        """Отметка уведомления как прочитанного"""
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            if notification:
                notification.is_read = True
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            self.db.rollback()
            return False

    def send_broadcast_to_users(self, broadcast: Broadcast) -> List[Notification]:
        """Отправка рассылки пользователям"""
        try:
            notifications = []
            users_query = self.db.query(User).filter(User.is_active == True)

            # Фильтрация пользователей в зависимости от типа рассылки
            if broadcast.broadcast_type == "department" and broadcast.target_department:
                users_query = users_query.filter(User.department == broadcast.target_department)
            elif broadcast.broadcast_type == "no_birthday":
                today = datetime.now()
                users_query = users_query.filter(
                    or_(
                        User.birthday.is_(None),
                        User.birthday != today
                    )
                )

            users = users_query.all()
            
            # Создание уведомлений для каждого пользователя
            for user in users:
                notification = self.create_notification(
                    user_id=user.id,
                    title=broadcast.title,
                    message=broadcast.message,
                    notification_type="broadcast"
                )
                notifications.append(notification)

            return notifications
        except Exception as e:
            logger.error(f"Error sending broadcast: {e}")
            self.db.rollback()
            return []

    def delete_old_notifications(self, days: int = 30) -> int:
        """Удаление старых уведомлений"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted = self.db.query(Notification).filter(
                Notification.created_at < cutoff_date
            ).delete()
            self.db.commit()
            return deleted
        except Exception as e:
            logger.error(f"Error deleting old notifications: {e}")
            self.db.rollback()
            return 0 
"""
Модуль планировщика задач для управления уведомлениями и рассылками.

Этот модуль отвечает за:
- Отправку напоминаний о днях рождения
- Контроль дедлайнов сборов
- Напоминания неплательщикам
- Управление запланированными рассылками
"""

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.birthday_service import get_upcoming_birthdays
from services.fund_service import get_funds_near_deadline
from services.user_service import get_admins
from database import SessionLocal
from models import User, Fund, Notification, Donation
from datetime import datetime, timedelta
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from config import REMINDER_HOUR, BIRTHDAY_REMINDER_DAYS, FUND_REMINDER_DAYS
import logging

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """
    Класс для управления запланированными задачами и уведомлениями.
    
    Attributes:
        scheduler (AsyncIOScheduler): Экземпляр планировщика задач
    """
    
    def __init__(self):
        """Инициализация планировщика и настройка задач."""
        self.scheduler = AsyncIOScheduler()
        self.setup_jobs()

    def setup_jobs(self):
        """
        Настройка всех запланированных задач.
        
        Добавляет следующие периодические задачи:
        - Проверка предстоящих дней рождения (ежедневно)
        - Проверка дедлайнов сборов (ежедневно)
        - Напоминания неплательщикам (ежедневно)
        - Отправка запланированных рассылок (каждые 5 минут)
        """
        # Ежедневные напоминания о днях рождения
        self.scheduler.add_job(
            self.check_upcoming_birthdays,
            CronTrigger(hour=REMINDER_HOUR),
            id='birthday_check',
            replace_existing=True
        )

        # Напоминания о сборах
        self.scheduler.add_job(
            self.check_fund_deadlines,
            CronTrigger(hour=REMINDER_HOUR),
            id='fund_check',
            replace_existing=True
        )

        # Напоминания неплательщикам
        self.scheduler.add_job(
            self.remind_unpaid_participants,
            CronTrigger(hour=REMINDER_HOUR),
            id='unpaid_reminder',
            replace_existing=True
        )

        # Отправка запланированных рассылок
        self.scheduler.add_job(
            self.send_scheduled_broadcasts,
            CronTrigger(minute='*/5'),  # Каждые 5 минут
            id='scheduled_broadcasts',
            replace_existing=True
        )

    async def check_upcoming_birthdays(self):
        """
        Проверка предстоящих дней рождения и отправка уведомлений.
        
        Находит пользователей, у которых день рождения наступит в ближайшие дни
        (количество дней определяется в BIRTHDAY_REMINDER_DAYS),
        и создает уведомления для администраторов.
        
        Raises:
            Exception: При ошибках доступа к БД или отправки уведомлений
        """
        try:
            db = SessionLocal()
            today = datetime.now()
            future_date = today + timedelta(days=BIRTHDAY_REMINDER_DAYS)

            upcoming_birthdays = db.query(User).filter(
                and_(
                    User.birthday.isnot(None),
                    User.is_active == True
                )
            ).all()

            for user in upcoming_birthdays:
                birthday_this_year = user.birthday.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until = (birthday_this_year - today).days
                if 0 <= days_until <= BIRTHDAY_REMINDER_DAYS:
                    self._create_birthday_notification(db, user, days_until)

        except Exception as e:
            logger.error(f"Error in birthday check: {e}")
        finally:
            db.close()

    async def check_fund_deadlines(self):
        """
        Проверка дедлайнов сборов и отправка уведомлений.
        
        Находит активные сборы с приближающимися дедлайнами
        (в пределах FUND_REMINDER_DAYS дней) и создает
        уведомления для казначеев.
        
        Raises:
            Exception: При ошибках доступа к БД или отправки уведомлений
        """
        try:
            db = SessionLocal()
            today = datetime.now()
            deadline_date = today + timedelta(days=FUND_REMINDER_DAYS)

            upcoming_deadlines = db.query(Fund).filter(
                and_(
                    Fund.is_active == True,
                    Fund.end_date <= deadline_date,
                    Fund.end_date > today
                )
            ).all()

            for fund in upcoming_deadlines:
                days_until = (fund.end_date - today).days
                self._create_fund_deadline_notification(db, fund, days_until)

        except Exception as e:
            logger.error(f"Error in fund deadline check: {e}")
        finally:
            db.close()

    async def remind_unpaid_participants(self):
        """
        Отправка напоминаний неплательщикам.
        
        Для каждого активного сбора находит пользователей,
        которые еще не внесли средства, и создает для них
        уведомления-напоминания.
        
        Raises:
            Exception: При ошибках доступа к БД или отправки уведомлений
        """
        try:
            db = SessionLocal()
            active_funds = db.query(Fund).filter(Fund.is_active == True).all()

            for fund in active_funds:
                paid_users = db.query(Donation.donor_id).filter(
                    Donation.fund_id == fund.id
                ).distinct().all()
                paid_user_ids = [user[0] for user in paid_users]

                unpaid_users = db.query(User).filter(
                    and_(
                        User.is_active == True,
                        ~User.id.in_(paid_user_ids)
                    )
                ).all()

                for user in unpaid_users:
                    self._create_unpaid_notification(db, fund, user)

        except Exception as e:
            logger.error(f"Error in unpaid reminder check: {e}")
        finally:
            db.close()

    async def send_scheduled_broadcasts(self):
        """
        Отправка запланированных рассылок.
        
        Находит все неотправленные уведомления, время отправки
        которых уже наступило, и отправляет их получателям.
        
        Raises:
            Exception: При ошибках доступа к БД или отправки уведомлений
        """
        try:
            db = SessionLocal()
            now = datetime.now()

            scheduled_notifications = db.query(Notification).filter(
                and_(
                    Notification.scheduled_for <= now,
                    Notification.is_read == False
                )
            ).all()

            for notification in scheduled_notifications:
                await self._send_notification(notification)
                notification.is_read = True

            db.commit()

        except Exception as e:
            logger.error(f"Error in scheduled broadcasts: {e}")
        finally:
            db.close()

    def _create_birthday_notification(self, db: Session, birthday_person: User, days_until: int):
        """
        Создание уведомления о предстоящем дне рождения.
        
        Args:
            db (Session): Сессия базы данных
            birthday_person (User): Пользователь, у которого скоро день рождения
            days_until (int): Количество дней до дня рождения
        """
        notification = Notification(
            user_id=birthday_person.id,
            title="Предстоящий день рождения",
            message=f"Через {days_until} дней день рождения у {birthday_person.full_name}",
            type="birthday",
            is_read=False
        )
        db.add(notification)
        db.commit()

    def _create_fund_deadline_notification(self, db: Session, fund: Fund, days_until: int):
        """
        Создание уведомления о дедлайне сбора.
        
        Args:
            db (Session): Сессия базы данных
            fund (Fund): Сбор, у которого приближается дедлайн
            days_until (int): Количество дней до дедлайна
        """
        notification = Notification(
            user_id=fund.treasurer_id,
            title="Дедлайн сбора",
            message=f"Через {days_until} дней заканчивается сбор '{fund.title}'",
            type="fund",
            is_read=False
        )
        db.add(notification)
        db.commit()

    def _create_unpaid_notification(self, db: Session, fund: Fund, user: User):
        """
        Создание уведомления о необходимости внести средства.
        
        Args:
            db (Session): Сессия базы данных
            fund (Fund): Сбор, в который нужно внести средства
            user (User): Пользователь, которому нужно напомнить о взносе
        """
        notification = Notification(
            user_id=user.id,
            title="Напоминание о сборе",
            message=f"Не забудьте внести средства в сбор '{fund.title}'",
            type="fund",
            is_read=False
        )
        db.add(notification)
        db.commit()

    async def _send_notification(self, notification: Notification):
        """
        Отправка уведомления пользователю.
        
        Args:
            notification (Notification): Уведомление для отправки
        
        Note:
            В текущей версии метод не реализован
        """
        # TODO: Реализовать отправку через бота
        pass

    def start(self):
        """Запуск планировщика задач."""
        self.scheduler.start()

    def shutdown(self):
        """Остановка планировщика задач."""
        self.scheduler.shutdown()

async def birthday_reminder(bot: Bot):
    """
    Отправка напоминаний о предстоящих днях рождения администраторам.
    
    Args:
        bot (Bot): Экземпляр бота для отправки сообщений
    """
    session = SessionLocal()
    try:
        birthdays = get_upcoming_birthdays()
        if not birthdays:
            return
        admins = get_admins()
        for staff in birthdays:
            text = f"🎂 Внимание! Через 10 дней день рождения: {staff.first_name} {staff.patronymic} ({staff.birthday.strftime('%d.%m.%Y')})"
            for admin in admins:
                try:
                    await bot.send_message(admin.telegram_id, text)
                except:
                    continue
    finally:
        session.close()

async def fund_deadline_reminder(bot: Bot):
    """
    Отправка напоминаний казначеям о приближающихся дедлайнах сборов.
    
    Args:
        bot (Bot): Экземпляр бота для отправки сообщений
    """
    session = SessionLocal()
    try:
        funds = get_funds_near_deadline()
        if not funds:
            return
        for fund in funds:
            treasurer: User = session.query(User).get(fund.treasury_user_id)
            if not treasurer:
                continue
            try:
                await bot.send_message(treasurer.telegram_id,
                    f"⏰ Напоминание: через {3} дня дедлайн по сбору №{fund.id}")
            except:
                continue
    finally:
        session.close()

def setup_scheduler(bot: Bot):
    """
    Настройка и запуск планировщика задач.
    
    Args:
        bot (Bot): Экземпляр бота для отправки сообщений
    
    Returns:
        AsyncIOScheduler: Настроенный экземпляр планировщика
    """
    scheduler = AsyncIOScheduler()
    scheduler.start()
    return scheduler

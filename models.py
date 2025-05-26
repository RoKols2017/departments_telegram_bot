"""
Модели данных SQLAlchemy для корпоративного Telegram-бота.
Описывают пользователей, роли, сборы, взносы, уведомления и рассылки.
"""
# models.py
from sqlalchemy import Column, Integer, BigInteger, String, Date, DateTime, Float, Boolean, ForeignKey, Text, Enum, JSON, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum
from datetime import datetime

Base = declarative_base()

class FundType(enum.Enum):
    """Типы сборов: день рождения или событие."""
    birthday = "birthday"
    event = "event"

class UserRole(enum.Enum):
    """Роли пользователей в системе."""
    USER = 1
    TREASURER = 2
    ADMIN = 3
    SUPERADMIN = 4

# Таблица для связи many-to-many между пользователями и ролями
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class Staff(Base):
    """Сотрудник компании (персональные данные, связь с User)."""
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    personnel_number = Column(Integer, unique=True, nullable=False)
    user = relationship("User", back_populates="staff", uselist=False)

class User(Base):
    """Пользователь Telegram-бота (привязан к Staff, имеет роли)."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    employee_id = Column(String, unique=True, nullable=False)  # Табельный номер
    full_name = Column(String)
    department = Column(String)
    birthday = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True, unique=True)
    staff = relationship("Staff", back_populates="user", uselist=False)
    
    # Отношения
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    managed_funds = relationship('Fund', back_populates='treasurer', foreign_keys='Fund.treasurer_id')
    birthday_funds = relationship('Fund', back_populates='birthday_person', foreign_keys='Fund.birthday_person_id')
    donations = relationship('Donation', back_populates='donor')
    logs = relationship('Log', back_populates='user')
    notifications = relationship('Notification', back_populates='user')
    broadcasts = relationship('Broadcast', back_populates='sender')

class Role(Base):
    """Роль пользователя (user, treasurer, admin, superadmin)."""
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    
    # Отношения
    users = relationship('User', secondary=user_roles, back_populates='roles')

class GiftFund(Base):
    """Сбор на подарок (ДР или событие), отдельная сущность для подарков."""
    __tablename__ = "gift_funds"
    id = Column(Integer, primary_key=True)
    type = Column(Enum(FundType), nullable=False)
    target_staff_id = Column(Integer, ForeignKey("staff.id"), nullable=True)
    event_name = Column(String, nullable=True)
    treasury_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    deadline = Column(Date, nullable=False)
    amount_expected = Column(Float, nullable=True)
    amount_collected = Column(Float, default=0)
    donations = Column(JSON, default=[])
    closed = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    target_staff = relationship("Staff", foreign_keys=[target_staff_id])
    treasury = relationship("User", foreign_keys=[treasury_user_id])

class Log(Base):
    """Лог действий пользователя."""
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="logs")

class Fund(Base):
    """Сбор средств (основная сущность для учёта взносов)."""
    __tablename__ = "funds"
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    start_date = Column(DateTime, default=func.now())
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    fund_type = Column(String, nullable=False)  # birthday, event
    birthday_person_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    treasurer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Отношения
    treasurer = relationship('User', back_populates='managed_funds', foreign_keys=[treasurer_id])
    birthday_person = relationship('User', back_populates='birthday_funds', foreign_keys=[birthday_person_id])
    donations = relationship('Donation', back_populates='fund')

class Donation(Base):
    """Взнос пользователя в сбор."""
    __tablename__ = "donations"
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    donor_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    donation_date = Column(DateTime, default=func.now())
    
    # Отношения
    fund = relationship('Fund', back_populates='donations')
    donor = relationship('User', back_populates='donations')

class Notification(Base):
    """Уведомление для пользователя (напоминания, рассылки)."""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, nullable=False)  # birthday, fund, system
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    scheduled_for = Column(DateTime)
    
    # Отношения
    user = relationship('User', back_populates='notifications')

class Broadcast(Base):
    """Рассылка сообщений пользователям."""
    __tablename__ = "broadcasts"
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    broadcast_type = Column(String, nullable=False)  # all, no_birthday, department
    target_department = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    scheduled_for = Column(DateTime, nullable=True)
    
    # Отношения
    sender = relationship('User', back_populates='broadcasts')
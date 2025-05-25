import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Role, Fund, Donation
from services.user_service import UserService
from services.fund_service import FundService
from datetime import datetime, timedelta

# Настройка тестовой БД
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user_service(db_session):
    return UserService(db_session)

@pytest.fixture
def fund_service(db_session):
    return FundService(db_session)

def test_create_user(user_service):
    user = user_service.create_user(
        telegram_id=123456,
        employee_id="123456",
        full_name="Test User"
    )
    assert user.telegram_id == 123456
    assert user.employee_id == "123456"
    assert user.full_name == "Test User"

def test_create_fund(fund_service, user_service):
    # Создаем казначея
    treasurer = user_service.create_user(
        telegram_id=123456,
        employee_id="123456"
    )
    
    # Создаем сбор
    fund = fund_service.create_fund(
        title="Test Fund",
        target_amount=1000.0,
        end_date=datetime.now() + timedelta(days=7),
        treasurer_id=treasurer.id,
        fund_type="event"
    )
    
    assert fund.title == "Test Fund"
    assert fund.target_amount == 1000.0
    assert fund.treasurer_id == treasurer.id

def test_add_donation(fund_service, user_service):
    # Создаем казначея и донора
    treasurer = user_service.create_user(telegram_id=123456, employee_id="123456")
    donor = user_service.create_user(telegram_id=789012, employee_id="789012")
    
    # Создаем сбор
    fund = fund_service.create_fund(
        title="Test Fund",
        target_amount=1000.0,
        end_date=datetime.now() + timedelta(days=7),
        treasurer_id=treasurer.id,
        fund_type="event"
    )
    
    # Добавляем взнос
    donation = fund_service.add_donation(
        fund_id=fund.id,
        donor_id=donor.id,
        amount=500.0
    )
    
    assert donation is not None
    assert donation.amount == 500.0
    assert donation.donor_id == donor.id 
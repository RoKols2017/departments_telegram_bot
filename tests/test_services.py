import sys
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base
from services.user_service import UserService
from services.fund_service import FundService
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Настройка тестовой БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(TEST_DATABASE_URL, future=True)
AsyncTestingSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncTestingSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def user_service(db_session):
    return UserService(db_session)


@pytest_asyncio.fixture
async def fund_service(db_session):
    return FundService(db_session)


@pytest.mark.asyncio
async def test_create_user(user_service):
    user = await user_service.create_user(
        telegram_id=123456,
        employee_id="123456",
        full_name="Test User"
    )
    assert user.telegram_id == 123456
    assert user.employee_id == "123456"
    assert user.full_name == "Test User"


@pytest.mark.asyncio
async def test_create_fund(fund_service, user_service):
    # Создаем казначея
    treasurer = await user_service.create_user(
        telegram_id=123456,
        employee_id="123456"
    )

    # Создаем сбор
    fund = await fund_service.create_fund(
        title="Test Fund",
        target_amount=1000.0,
        end_date=datetime.now() + timedelta(days=7),
        treasurer_id=treasurer.id,
        fund_type="event",
    )

    assert fund.title == "Test Fund"
    assert fund.target_amount == 1000.0
    assert fund.treasurer_id == treasurer.id


@pytest.mark.asyncio
async def test_add_donation(fund_service, user_service):
    # Создаем казначея и донора
    treasurer = await user_service.create_user(telegram_id=123456, employee_id="123456")
    donor = await user_service.create_user(telegram_id=789012, employee_id="789012")

    # Создаем сбор
    fund = await fund_service.create_fund(
        title="Test Fund",
        target_amount=1000.0,
        end_date=datetime.now() + timedelta(days=7),
        treasurer_id=treasurer.id,
        fund_type="event",
    )

    # Добавляем взнос
    donation = await fund_service.add_donation(
        fund_id=fund.id,
        donor_id=donor.id,
        amount=500.0
    )

    assert donation is not None
    assert donation.amount == 500.0
    assert donation.donor_id == donor.id

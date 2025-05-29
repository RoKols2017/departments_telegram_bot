"""
Сервис для управления сборами: создание, поиск, взносы, статус, напоминания.
"""

# services/fund_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from models import Fund, User, Donation
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FundService:
    """
    Сервис для работы со сборами (создание, поиск, взносы, напоминания).
    Использует SQLAlchemy-сессию для всех операций с БД.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_fund(
        self,
        title: str,
        target_amount: float,
        end_date: datetime,
        treasurer_id: int,
        fund_type: str,
        birthday_person_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Fund:
        """Создание нового сбора"""
        try:
            # Проверяем, что казначей не является именинником
            if fund_type == "birthday" and treasurer_id == birthday_person_id:
                raise ValueError("Казначей не может быть именинником")

            fund = Fund(
                title=title,
                description=description,
                target_amount=target_amount,
                end_date=end_date,
                treasurer_id=treasurer_id,
                fund_type=fund_type,
                birthday_person_id=birthday_person_id,
                is_active=True,
            )
            self.db.add(fund)
            await self.db.commit()
            await self.db.refresh(fund)
            return fund
        except Exception as e:
            logger.error(f"Error creating fund: {e}")
            await self.db.rollback()
            raise

    async def get_fund(self, fund_id: int) -> Optional[Fund]:
        """Получение сбора по ID"""
        result = await self.db.execute(select(Fund).where(Fund.id == fund_id))
        return result.scalar_one_or_none()

    async def get_active_funds(self) -> List[Fund]:
        """Получение всех активных сборов"""
        result = await self.db.execute(select(Fund).where(Fund.is_active.is_(True)))
        return result.scalars().all()

    async def get_funds_by_treasurer(self, treasurer_id: int) -> List[Fund]:
        """Получение сборов по казначею"""
        result = await self.db.execute(
            select(Fund).where(
                and_(Fund.treasurer_id == treasurer_id, Fund.is_active.is_(True))
            )
        )
        return result.scalars().all()

    async def get_birthday_funds(self) -> List[Fund]:
        """Получение сборов на дни рождения"""
        result = await self.db.execute(
            select(Fund).where(
                and_(Fund.fund_type == "birthday", Fund.is_active.is_(True))
            )
        )
        return result.scalars().all()

    async def close_fund(self, fund_id: int) -> bool:
        """Закрытие сбора"""
        try:
            fund = await self.get_fund(fund_id)
            if fund:
                fund.is_active = False
                await self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error closing fund: {e}")
            await self.db.rollback()
            return False

    async def add_donation(
        self, fund_id: int, donor_id: int, amount: float
    ) -> Optional[Donation]:
        """Добавление взноса в сбор"""
        try:
            fund = await self.get_fund(fund_id)
            if not fund or not fund.is_active:
                return None

            donation = Donation(fund_id=fund_id, donor_id=donor_id, amount=amount)
            self.db.add(donation)

            # Обновляем текущую сумму сбора
            fund.current_amount = fund.current_amount + amount

            await self.db.commit()
            await self.db.refresh(donation)
            return donation
        except Exception as e:
            logger.error(f"Error adding donation: {e}")
            await self.db.rollback()
            return None

    async def get_fund_status(self, fund_id: int) -> Dict:
        """Получение статуса сбора"""
        fund = await self.get_fund(fund_id)
        if not fund:
            return {}

        result = await self.db.execute(
            select(Donation).where(Donation.fund_id == fund_id)
        )
        donations = result.scalars().all()
        donors = set(d.donor_id for d in donations)

        return {
            "title": fund.title,
            "target_amount": fund.target_amount,
            "current_amount": fund.current_amount,
            "remaining_amount": fund.target_amount - fund.current_amount,
            "donors_count": len(donors),
            "is_active": fund.is_active,
            "days_left": (fund.end_date - datetime.now()).days,
        }

    async def get_unpaid_users(self, fund_id: int) -> List[User]:
        """Получение списка пользователей, не сделавших взнос"""
        fund = await self.get_fund(fund_id)
        if not fund:
            return []

        # Получаем ID всех, кто уже сделал взнос
        paid_result = await self.db.execute(
            select(Donation.donor_id).where(Donation.fund_id == fund_id).distinct()
        )
        paid_user_ids = [user_id for (user_id,) in paid_result.all()]

        # Получаем всех активных пользователей, кто еще не сделал взнос
        result = await self.db.execute(
            select(User).where(
                and_(User.is_active.is_(True), ~User.id.in_(paid_user_ids))
            )
        )
        return result.scalars().all()

    async def get_user_donations(self, user_id: int) -> List[Dict]:
        """Получение всех взносов пользователя"""
        result = await self.db.execute(
            select(Donation).where(Donation.donor_id == user_id)
        )
        donations = result.scalars().all()

        res = []
        for donation in donations:
            fund = await self.get_fund(donation.fund_id)
            res.append(
                {
                    "fund_title": fund.title if fund else None,
                    "amount": donation.amount,
                    "date": donation.donation_date,
                    "fund_type": fund.fund_type if fund else None,
                }
            )

        return res

    async def get_funds_near_deadline(self, days: int = 3) -> List[Fund]:
        """Получение сборов с дедлайном в ближайшие days дней"""
        today = datetime.now()
        deadline_date = today + timedelta(days=days)
        result = await self.db.execute(
            select(Fund).where(
                and_(
                    Fund.is_active.is_(True),
                    Fund.end_date <= deadline_date,
                    Fund.end_date > today,
                )
            )
        )
        return result.scalars().all()

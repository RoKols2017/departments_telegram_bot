"""
Сервис для управления сборами: создание, поиск, взносы, статус, напоминания.
"""
# services/fund_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
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
    def __init__(self, db: Session):
        self.db = db

    def create_fund(
        self,
        title: str,
        target_amount: float,
        end_date: datetime,
        treasurer_id: int,
        fund_type: str,
        birthday_person_id: Optional[int] = None,
        description: Optional[str] = None
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
                is_active=True
            )
            self.db.add(fund)
            self.db.commit()
            self.db.refresh(fund)
            return fund
        except Exception as e:
            logger.error(f"Error creating fund: {e}")
            self.db.rollback()
            raise

    def get_fund(self, fund_id: int) -> Optional[Fund]:
        """Получение сбора по ID"""
        return self.db.query(Fund).filter(Fund.id == fund_id).first()

    def get_active_funds(self) -> List[Fund]:
        """Получение всех активных сборов"""
        return self.db.query(Fund).filter(Fund.is_active == True).all()

    def get_funds_by_treasurer(self, treasurer_id: int) -> List[Fund]:
        """Получение сборов по казначею"""
        return self.db.query(Fund).filter(
            and_(
                Fund.treasurer_id == treasurer_id,
                Fund.is_active == True
            )
        ).all()

    def get_birthday_funds(self) -> List[Fund]:
        """Получение сборов на дни рождения"""
        return self.db.query(Fund).filter(
            and_(
                Fund.fund_type == "birthday",
                Fund.is_active == True
            )
        ).all()

    def close_fund(self, fund_id: int) -> bool:
        """Закрытие сбора"""
        try:
            fund = self.get_fund(fund_id)
            if fund:
                fund.is_active = False
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error closing fund: {e}")
            self.db.rollback()
            return False

    def add_donation(self, fund_id: int, donor_id: int, amount: float) -> Optional[Donation]:
        """Добавление взноса в сбор"""
        try:
            fund = self.get_fund(fund_id)
            if not fund or not fund.is_active:
                return None

            donation = Donation(
                fund_id=fund_id,
                donor_id=donor_id,
                amount=amount
            )
            self.db.add(donation)
            
            # Обновляем текущую сумму сбора
            fund.current_amount = fund.current_amount + amount
            
            self.db.commit()
            self.db.refresh(donation)
            return donation
        except Exception as e:
            logger.error(f"Error adding donation: {e}")
            self.db.rollback()
            return None

    def get_fund_status(self, fund_id: int) -> Dict:
        """Получение статуса сбора"""
        fund = self.get_fund(fund_id)
        if not fund:
            return {}

        donations = self.db.query(Donation).filter(Donation.fund_id == fund_id).all()
        donors = set(d.donor_id for d in donations)
        
        return {
            "title": fund.title,
            "target_amount": fund.target_amount,
            "current_amount": fund.current_amount,
            "remaining_amount": fund.target_amount - fund.current_amount,
            "donors_count": len(donors),
            "is_active": fund.is_active,
            "days_left": (fund.end_date - datetime.now()).days
        }

    def get_unpaid_users(self, fund_id: int) -> List[User]:
        """Получение списка пользователей, не сделавших взнос"""
        fund = self.get_fund(fund_id)
        if not fund:
            return []

        # Получаем ID всех, кто уже сделал взнос
        paid_users = self.db.query(Donation.donor_id).filter(
            Donation.fund_id == fund_id
        ).distinct().all()
        paid_user_ids = [user[0] for user in paid_users]

        # Получаем всех активных пользователей, кто еще не сделал взнос
        return self.db.query(User).filter(
            and_(
                User.is_active == True,
                ~User.id.in_(paid_user_ids)
            )
        ).all()

    def get_user_donations(self, user_id: int) -> List[Dict]:
        """Получение всех взносов пользователя"""
        donations = self.db.query(Donation).filter(
            Donation.donor_id == user_id
        ).all()

        result = []
        for donation in donations:
            fund = self.get_fund(donation.fund_id)
            result.append({
                "fund_title": fund.title,
                "amount": donation.amount,
                "date": donation.donation_date,
                "fund_type": fund.fund_type
            })
        
        return result

    def get_funds_near_deadline(self, days: int = 3) -> List[Fund]:
        """Получение сборов с дедлайном в ближайшие days дней"""
        today = datetime.now()
        deadline_date = today + timedelta(days=days)
        return self.db.query(Fund).filter(
            and_(
                Fund.is_active == True,
                Fund.end_date <= deadline_date,
                Fund.end_date > today
            )
        ).all()

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.plan import Plan
from app.models.user import User
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate
from app.core.exceptions import NotFoundException, BadRequestException, ConflictException


class SubscriptionService:
    
    @staticmethod
    async def create_subscription(db: AsyncSession, subscription_data: SubscriptionCreate) -> Subscription:
        """Create a new subscription"""
        # Verify user exists
        user_result = await db.execute(select(User).where(User.id == subscription_data.user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")
        
        # Verify plan exists and is active
        plan_result = await db.execute(select(Plan).where(
            and_(Plan.id == subscription_data.plan_id, Plan.is_active == True)
        ))
        plan = plan_result.scalar_one_or_none()
        if not plan:
            raise NotFoundException("Plan not found or inactive")
        
        # Check if user already has an active subscription
        existing_subscription = await SubscriptionService.get_active_subscription_by_user(
            db, subscription_data.user_id
        )
        if existing_subscription:
            raise ConflictException("User already has an active subscription")
        
        # Calculate end date based on plan duration
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=plan.duration_days)
        
        db_subscription = Subscription(
            user_id=subscription_data.user_id,
            plan_id=subscription_data.plan_id,
            start_date=start_date,
            end_date=end_date,
            auto_renew=subscription_data.auto_renew,
            status=SubscriptionStatus.ACTIVE
        )
        
        db.add(db_subscription)
        await db.commit()
        await db.refresh(db_subscription)
        return db_subscription
    
    @staticmethod
    async def get_subscription_by_id(db: AsyncSession, subscription_id: int) -> Optional[Subscription]:
        """Get subscription by ID with related data"""
        result = await db.execute(
            select(Subscription)
            .options(selectinload(Subscription.plan), selectinload(Subscription.user))
            .where(Subscription.id == subscription_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_subscription_by_user(db: AsyncSession, user_id: int) -> Optional[Subscription]:
        """Get user's current subscription"""
        result = await db.execute(
            select(Subscription)
            .options(selectinload(Subscription.plan), selectinload(Subscription.user))
            .where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.INACTIVE])
                )
            )
            .order_by(Subscription.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_active_subscription_by_user(db: AsyncSession, user_id: int) -> Optional[Subscription]:
        """Get user's active subscription"""
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.user_id == user_id,
                    Subscription.status == SubscriptionStatus.ACTIVE
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_subscription(
        db: AsyncSession, 
        user_id: int, 
        subscription_data: SubscriptionUpdate
    ) -> Subscription:
        """Update user's subscription"""
        subscription = await SubscriptionService.get_active_subscription_by_user(db, user_id)
        if not subscription:
            raise NotFoundException("No active subscription found for user")
        
        update_data = subscription_data.model_dump(exclude_unset=True)
        
        # Handle plan change
        if "plan_id" in update_data:
            plan_result = await db.execute(select(Plan).where(
                and_(Plan.id == update_data["plan_id"], Plan.is_active == True)
            ))
            plan = plan_result.scalar_one_or_none()
            if not plan:
                raise NotFoundException("Plan not found or inactive")
            
            # Recalculate end date if plan changed
            current_plan_result = await db.execute(select(Plan).where(Plan.id == subscription.plan_id))
            current_plan = current_plan_result.scalar_one()
            
            if plan.duration_days != current_plan.duration_days:
                remaining_time = subscription.end_date - datetime.utcnow()
                subscription.end_date = datetime.utcnow() + timedelta(days=plan.duration_days)
        
        # Apply updates
        for field, value in update_data.items():
            setattr(subscription, field, value)
        
        await db.commit()
        await db.refresh(subscription)
        return subscription
    
    @staticmethod
    async def cancel_subscription(db: AsyncSession, user_id: int) -> Subscription:
        """Cancel user's subscription"""
        subscription = await SubscriptionService.get_active_subscription_by_user(db, user_id)
        if not subscription:
            raise NotFoundException("No active subscription found for user")
        
        subscription.status = SubscriptionStatus.CANCELLED
        subscription.auto_renew = False
        
        await db.commit()
        await db.refresh(subscription)
        return subscription
    
    @staticmethod
    async def expire_subscriptions(db: AsyncSession) -> int:
        """Expire subscriptions that have passed their end date"""
        current_time = datetime.utcnow()
        
        result = await db.execute(
            select(Subscription).where(
                and_(
                    Subscription.status == SubscriptionStatus.ACTIVE,
                    Subscription.end_date <= current_time
                )
            )
        )
        expired_subscriptions = result.scalars().all()
        
        count = 0
        for subscription in expired_subscriptions:
            subscription.status = SubscriptionStatus.EXPIRED
            count += 1
        
        if count > 0:
            await db.commit()
        
        return count
    
    @staticmethod
    async def get_all_subscriptions(
        db: AsyncSession, 
        status: Optional[SubscriptionStatus] = None
    ) -> List[Subscription]:
        """Get all subscriptions, optionally filtered by status"""
        query = select(Subscription).options(
            selectinload(Subscription.plan), 
            selectinload(Subscription.user)
        )
        
        if status:
            query = query.where(Subscription.status == status)
        
        result = await db.execute(query)
        return result.scalars().all() 
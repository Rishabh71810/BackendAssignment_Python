from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.plan import Plan
from app.schemas.plan import PlanCreate, PlanUpdate
from app.core.exceptions import NotFoundException, ConflictException


class PlanService:
    
    @staticmethod
    async def create_plan(db: AsyncSession, plan_data: PlanCreate) -> Plan:
        """Create a new subscription plan"""
        # Check if plan with same name exists
        existing_plan = await PlanService.get_plan_by_name(db, plan_data.name)
        if existing_plan:
            raise ConflictException("Plan with this name already exists")
        
        db_plan = Plan(**plan_data.model_dump())
        db.add(db_plan)
        await db.commit()
        await db.refresh(db_plan)
        return db_plan
    
    @staticmethod
    async def get_plan_by_id(db: AsyncSession, plan_id: int) -> Optional[Plan]:
        """Get plan by ID"""
        result = await db.execute(select(Plan).where(Plan.id == plan_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_plan_by_name(db: AsyncSession, name: str) -> Optional[Plan]:
        """Get plan by name"""
        result = await db.execute(select(Plan).where(Plan.name == name))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_plans(db: AsyncSession, include_inactive: bool = False) -> List[Plan]:
        """Get all plans"""
        if include_inactive:
            result = await db.execute(select(Plan))
        else:
            result = await db.execute(select(Plan).where(Plan.is_active == True))
        return result.scalars().all()
    
    @staticmethod
    async def update_plan(db: AsyncSession, plan_id: int, plan_data: PlanUpdate) -> Plan:
        """Update plan information"""
        plan = await PlanService.get_plan_by_id(db, plan_id)
        if not plan:
            raise NotFoundException("Plan not found")
        
        update_data = plan_data.model_dump(exclude_unset=True)
        
        # Check name uniqueness if name is being updated
        if "name" in update_data and update_data["name"] != plan.name:
            existing_plan = await PlanService.get_plan_by_name(db, update_data["name"])
            if existing_plan:
                raise ConflictException("Plan with this name already exists")
        
        for field, value in update_data.items():
            setattr(plan, field, value)
        
        await db.commit()
        await db.refresh(plan)
        return plan
    
    @staticmethod
    async def delete_plan(db: AsyncSession, plan_id: int) -> bool:
        """Soft delete plan by setting is_active to False"""
        plan = await PlanService.get_plan_by_id(db, plan_id)
        if not plan:
            raise NotFoundException("Plan not found")
        
        plan.is_active = False
        await db.commit()
        return True 
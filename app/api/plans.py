from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.plan import PlanResponse, PlanCreate, PlanUpdate
from app.services.plan_service import PlanService
from app.models.user import User
from app.core.auth import get_current_active_user

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.get("", response_model=List[PlanResponse])
async def get_all_plans(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Get all available subscription plans"""
    return await PlanService.get_all_plans(db, include_inactive=include_inactive)


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: PlanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new subscription plan (Admin only)"""
    return await PlanService.create_plan(db, plan_data)


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get plan details by ID"""
    plan = await PlanService.get_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a subscription plan (Admin only)"""
    return await PlanService.update_plan(db, plan_id, plan_data)


@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Soft delete a subscription plan (Admin only)"""
    await PlanService.delete_plan(db, plan_id)
    return {"message": "Plan deleted successfully"} 
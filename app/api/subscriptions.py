from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.subscription import (
    SubscriptionCreate, 
    SubscriptionResponse, 
    SubscriptionDetailResponse,
    SubscriptionUpdate
)
from app.services.subscription_service import SubscriptionService
from app.models.user import User
from app.models.subscription import SubscriptionStatus
from app.core.auth import get_current_active_user

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("", response_model=SubscriptionDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new subscription"""
    # Only allow users to create their own subscriptions unless admin
    if subscription_data.user_id != current_user.id:
        subscription_data.user_id = current_user.id
    
    subscription = await SubscriptionService.create_subscription(db, subscription_data)
    return await SubscriptionService.get_subscription_by_id(db, subscription.id)


@router.get("/{user_id}", response_model=SubscriptionDetailResponse)
async def get_user_subscription(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve a user's current subscription"""
    # Users can only access their own subscriptions
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this subscription"
        )
    
    subscription = await SubscriptionService.get_subscription_by_user(db, user_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found for user"
        )
    
    return subscription


@router.put("/{user_id}", response_model=SubscriptionDetailResponse)
async def update_user_subscription(
    user_id: int,
    subscription_data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a user's subscription"""
    # Users can only update their own subscriptions
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this subscription"
        )
    
    subscription = await SubscriptionService.update_subscription(db, user_id, subscription_data)
    return await SubscriptionService.get_subscription_by_id(db, subscription.id)


@router.delete("/{user_id}")
async def cancel_user_subscription(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel a user's subscription"""
    # Users can only cancel their own subscriptions
    if user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this subscription"
        )
    
    await SubscriptionService.cancel_subscription(db, user_id)
    return {"message": "Subscription cancelled successfully"}


@router.get("", response_model=List[SubscriptionDetailResponse])
async def get_all_subscriptions(
    status_filter: Optional[SubscriptionStatus] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all subscriptions (Admin only)"""
    return await SubscriptionService.get_all_subscriptions(db, status=status_filter)


@router.post("/expire", status_code=status.HTTP_200_OK)
async def expire_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Manually trigger subscription expiration check (Admin only)"""
    count = await SubscriptionService.expire_subscriptions(db)
    return {"message": f"Expired {count} subscriptions"} 
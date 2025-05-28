from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionStatus
from app.schemas.plan import PlanResponse
from app.schemas.user import UserResponse


class SubscriptionBase(BaseModel):
    plan_id: int
    auto_renew: Optional[bool] = True


class SubscriptionCreate(SubscriptionBase):
    user_id: int


class SubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    auto_renew: Optional[bool] = None
    status: Optional[SubscriptionStatus] = None


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: SubscriptionStatus
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubscriptionDetailResponse(SubscriptionResponse):
    plan: Optional[PlanResponse] = None
    user: Optional[UserResponse] = None 
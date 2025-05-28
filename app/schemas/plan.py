from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PlanBase(BaseModel):
    name: str
    price: Decimal
    features: Optional[str] = None
    duration_days: int
    description: Optional[str] = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[Decimal] = None
    features: Optional[str] = None
    duration_days: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PlanResponse(PlanBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 
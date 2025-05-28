from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.auth import get_password_hash
from app.core.exceptions import NotFoundException, ConflictException


class UserService:
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise ConflictException("User with this email already exists")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
        """Update user information"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # Handle password update
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        # Check email uniqueness if email is being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing_user = await UserService.get_user_by_email(db, update_data["email"])
            if existing_user:
                raise ConflictException("User with this email already exists")
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Soft delete user by setting is_active to False"""
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException("User not found")
        
        user.is_active = False
        await db.commit()
        return True 
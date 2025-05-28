#!/usr/bin/env python3
"""
Script to seed the database with sample plans and test data.
"""

import asyncio
from decimal import Decimal
from app.database import AsyncSessionLocal
from app.models.plan import Plan
from app.models.user import User
from app.core.auth import get_password_hash


async def seed_plans():
    """Seed database with sample subscription plans"""
    plans_data = [
        {
            "name": "Basic",
            "price": Decimal("9.99"),
            "features": "Basic features: 10 projects, 1GB storage, Email support",
            "duration_days": 30,
            "description": "Perfect for individuals getting started"
        },
        {
            "name": "Pro",
            "price": Decimal("29.99"),
            "features": "Pro features: 100 projects, 10GB storage, Priority support, Advanced analytics",
            "duration_days": 30,
            "description": "Great for growing businesses"
        },
        {
            "name": "Enterprise",
            "price": Decimal("99.99"),
            "features": "Enterprise features: Unlimited projects, 100GB storage, 24/7 support, Custom integrations",
            "duration_days": 30,
            "description": "For large organizations with advanced needs"
        },
        {
            "name": "Annual Basic",
            "price": Decimal("99.99"),
            "features": "Basic features: 10 projects, 1GB storage, Email support",
            "duration_days": 365,
            "description": "Basic plan with annual billing (2 months free)"
        }
    ]
    
    async with AsyncSessionLocal() as db:
        for plan_data in plans_data:
            # Check if plan already exists
            from sqlalchemy import select
            result = await db.execute(select(Plan).where(Plan.name == plan_data["name"]))
            existing_plan = result.scalar_one_or_none()
            
            if not existing_plan:
                plan = Plan(**plan_data)
                db.add(plan)
                print(f"Added plan: {plan_data['name']}")
            else:
                print(f"Plan {plan_data['name']} already exists")
        
        await db.commit()


async def seed_test_user():
    """Create a test user for development"""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        # Check if test user already exists
        result = await db.execute(select(User).where(User.email == "test@example.com"))
        existing_user = result.scalar_one_or_none()
        
        if not existing_user:
            test_user = User(
                email="test@example.com",
                hashed_password=get_password_hash("testpassword"),
                full_name="Test User"
            )
            db.add(test_user)
            await db.commit()
            print("Created test user: test@example.com (password: testpassword)")
        else:
            print("Test user already exists")


async def main():
    """Run all seeding functions"""
    print("Seeding database with sample data...")
    await seed_plans()
    await seed_test_user()
    print("Database seeding completed!")


if __name__ == "__main__":
    asyncio.run(main()) 
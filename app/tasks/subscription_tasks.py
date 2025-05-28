import asyncio
from celery import Celery
from app.tasks.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.services.subscription_service import SubscriptionService


@celery_app.task
def expire_subscriptions_task():
    """Background task to expire subscriptions"""
    async def _expire_subscriptions():
        async with AsyncSessionLocal() as db:
            count = await SubscriptionService.expire_subscriptions(db)
            return count
    
    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        count = loop.run_until_complete(_expire_subscriptions())
        return f"Expired {count} subscriptions"
    finally:
        loop.close()


@celery_app.task
def send_subscription_notification(user_email: str, subscription_id: int, notification_type: str):
    """Background task to send subscription notifications"""
    # This is a placeholder for sending notifications
    # In a real implementation, you would integrate with an email service
    print(f"Sending {notification_type} notification to {user_email} for subscription {subscription_id}")
    return f"Notification sent to {user_email}"


@celery_app.task
def process_subscription_renewal(subscription_id: int):
    """Background task to process subscription renewals"""
    async def _process_renewal():
        async with AsyncSessionLocal() as db:
            # This is a placeholder for renewal logic
            # In a real implementation, you would integrate with payment processing
            subscription = await SubscriptionService.get_subscription_by_id(db, subscription_id)
            if subscription and subscription.auto_renew:
                # Process payment and extend subscription
                print(f"Processing renewal for subscription {subscription_id}")
                return True
            return False
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_process_renewal())
        return f"Renewal processed: {result}"
    finally:
        loop.close() 
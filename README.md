# Subscription Management Service

A microservice for managing user subscriptions to various SaaS plans, built with FastAPI, PostgreSQL, and modern Python practices.

## Features

- 🔐 JWT Authentication
- 📊 Subscription Management (Create, Read, Update, Cancel)
- 💳 Plan Management
- 🔄 Automatic Subscription Expiration
- 🎯 RESTful API Design
- 🧪 Comprehensive Test Suite
- 📚 Auto-generated API Documentation
- 🔄 Background Task Processing with Celery
- 🐘 PostgreSQL with Async SQLAlchemy
- 🏗️ Clean Architecture Pattern

## Technology Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with AsyncPG
- **ORM**: SQLAlchemy 2.0 (Async)
- **Authentication**: JWT with passlib
- **Task Queue**: Celery with Redis
- **Testing**: Pytest with httpx
- **Migration**: Alembic
- **Environment**: Python 3.8+

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Plans
- `GET /plans` - Get all available subscription plans
- `POST /plans` - Create a new plan (Admin)
- `GET /plans/{plan_id}` - Get plan details
- `PUT /plans/{plan_id}` - Update plan (Admin)
- `DELETE /plans/{plan_id}` - Delete plan (Admin)

### Subscriptions
- `POST /subscriptions` - Create a new subscription
- `GET /subscriptions/{user_id}` - Get user's current subscription
- `PUT /subscriptions/{user_id}` - Update user's subscription
- `DELETE /subscriptions/{user_id}` - Cancel user's subscription
- `GET /subscriptions` - Get all subscriptions (Admin)
- `POST /subscriptions/expire` - Manually expire subscriptions (Admin)

### Health
- `GET /` - Service health check
- `GET /health` - Detailed health status

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (for Celery tasks)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd subscription-service
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your database and Redis configuration
   ```

5. **Set up the database**
   ```bash
   # Create database
   createdb subscription_db
   
   # Run migrations
   alembic upgrade head
   
   # Seed with sample data (optional)
   python scripts/seed_data.py
   ```

6. **Run the service**
   ```bash
   # Development server
   python scripts/run_server.py
   
   # Or with uvicorn directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start Celery worker (optional)**
   ```bash
   # In a separate terminal
   celery -A app.tasks.celery_app worker --loglevel=info
   
   # For scheduled tasks
   celery -A app.tasks.celery_app beat --loglevel=info
   ```

### Using the API

1. **Register a user**
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{
          "email": "user@example.com",
          "password": "securepassword",
          "full_name": "John Doe"
        }'
   ```

2. **Login to get access token**
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=user@example.com&password=securepassword"
   ```

3. **Get available plans**
   ```bash
   curl -X GET "http://localhost:8000/plans"
   ```

4. **Create a subscription** (requires authentication)
   ```bash
   curl -X POST "http://localhost:8000/subscriptions" \
        -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
          "user_id": 1,
          "plan_id": 1,
          "auto_renew": true
        }'
   ```

## Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique)
- `hashed_password`
- `full_name`
- `is_active`
- `created_at`
- `updated_at`

### Plans Table
- `id` (Primary Key)
- `name` (Unique)
- `price`
- `features` (JSON string)
- `duration_days`
- `description`
- `is_active`
- `created_at`
- `updated_at`

### Subscriptions Table
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `plan_id` (Foreign Key)
- `status` (ENUM: ACTIVE, INACTIVE, CANCELLED, EXPIRED)
- `start_date`
- `end_date`
- `auto_renew`
- `created_at`
- `updated_at`

## Testing

Run the test suite:

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/subscription_db` |
| `SECRET_KEY` | JWT secret key | `your-super-secret-key-change-this-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `ENVIRONMENT` | Environment (development/production) | `development` |

## API Documentation

Once the service is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

The service follows Clean Architecture principles:

```
app/
├── api/           # API routes and endpoints
├── core/          # Core business logic and utilities
├── models/        # Database models
├── schemas/       # Pydantic schemas for validation
├── services/      # Business logic services
├── tasks/         # Background tasks (Celery)
└── main.py        # FastAPI application setup
```

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. Use environment variables for sensitive configuration
2. Set up proper logging
3. Configure CORS for your frontend domains
4. Use a reverse proxy (Nginx) in front of the service
5. Set up monitoring and health checks
6. Use a production WSGI server like Gunicorn
7. Implement proper backup strategies for PostgreSQL
8. Set up SSL/TLS certificates

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy
- CORS middleware configuration
- Environment-based configuration

## Performance Features

- Async/await throughout the application
- Connection pooling with SQLAlchemy
- Background task processing with Celery
- Efficient database queries with eager loading
- Proper indexing on database tables

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the repository or contact the development team. #   B a c k e n d A s s i g n m e n t _ P y t h o n  
 
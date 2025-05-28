import pytest
from httpx import AsyncClient


class TestAPI:
    
    async def test_health_check(self, client: AsyncClient):
        """Test the health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "subscription-management"
    
    async def test_root_endpoint(self, client: AsyncClient):
        """Test the root endpoint"""
        response = await client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "Subscription Management Service" in data["message"]
        assert data["status"] == "healthy"
    
    async def test_get_plans_without_auth(self, client: AsyncClient):
        """Test getting plans without authentication (should work)"""
        response = await client.get("/plans")
        assert response.status_code == 200
        assert isinstance(response.json(), list) 
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session


@pytest.mark.asyncio
async def test_health_check(test_client: AsyncClient) -> None:
    """Test the health check endpoint."""
    response = await test_client.get("/api/health/check")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is healthy"}


@pytest.mark.asyncio
async def test_create_and_get_items(test_client: AsyncClient, test_db: Session) -> None:
    """Test creating and retrieving test items."""
    # Create a test item
    test_item = {"name": "Test Item"}
    response = await test_client.post("/api/test/item", json=test_item)
    assert response.status_code == 200
    created_item = response.json()
    assert created_item["name"] == test_item["name"]
    assert "id" in created_item

    # Get all items
    response = await test_client.get("/api/test/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    assert any(item["name"] == test_item["name"] for item in items)

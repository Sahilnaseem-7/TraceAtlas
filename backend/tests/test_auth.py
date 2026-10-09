import pytest

@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "password123",
        "full_name": "New User"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"

@pytest.mark.asyncio
async def test_login(client, test_user):
    response = await client.post("/api/auth/login", params={"email": "test@example.com", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
import pytest


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/api/auth/register", json={
        "email": "new@example.com",
        "password": "password123",
        "full_name": "New User",
    })
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_register_rejects_short_password(client):
    response = await client.post("/api/auth/register", json={
        "email": "short@example.com",
        "password": "123",
        "full_name": "Short Password",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login(client, test_user):
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_rejects_bad_password(client, test_user):
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401

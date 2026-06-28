import pytest


async def test_register(client):
    response = await client.post("/auth/register", json={
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "password123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data


async def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "full_name": "User",
        "password": "password123"
    }
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400


async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "full_name": "Login User",
        "password": "password123"
    })
    response = await client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "wrong@example.com",
        "full_name": "Wrong User",
        "password": "correctpass"
    })
    response = await client.post("/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401


async def test_me_authenticated(auth_client):
    response = await auth_client.get("/me")
    assert response.status_code == 200
    assert "email" in response.json()


async def test_me_unauthenticated(client):
    response = await client.get("/me")
    assert response.status_code == 401
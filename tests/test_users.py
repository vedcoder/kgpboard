"""Tests for user registration and listing."""


async def test_register_user_success(client):
    resp = await client.post(
        "/users",
        json={"name": "Asha", "email": "asha@test.com", "password": "password1"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "asha@test.com"
    assert body["role"] == "student"  # public sign-up is always a student
    assert "createdAt" in body
    # The password (and its hash) must never be exposed.
    assert "password" not in body
    assert "passwordHash" not in body


async def test_register_missing_name_returns_400(client):
    resp = await client.post(
        "/users", json={"email": "a@test.com", "password": "password1"}
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["detail"] == "Validation failed."
    assert "name" in [e["field"] for e in body["errors"]]


async def test_register_invalid_email_returns_400(client):
    resp = await client.post(
        "/users", json={"name": "A", "email": "not-an-email", "password": "password1"}
    )
    assert resp.status_code == 400
    assert "email" in [e["field"] for e in resp.json()["errors"]]


async def test_register_short_password_returns_400(client):
    resp = await client.post(
        "/users", json={"name": "A", "email": "a@test.com", "password": "short"}
    )
    assert resp.status_code == 400


async def test_duplicate_email_returns_409(client):
    payload = {"name": "A", "email": "dup@test.com", "password": "password1"}
    await client.post("/users", json=payload)
    resp = await client.post("/users", json=payload)
    assert resp.status_code == 409
    assert "already exists" in resp.json()["detail"]


async def test_list_users_pagination_envelope(client):
    for i in range(3):
        await client.post(
            "/users",
            json={"name": f"U{i}", "email": f"u{i}@test.com", "password": "password1"},
        )
    resp = await client.get("/users", params={"limit": 2, "offset": 0})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    assert body["limit"] == 2
    assert len(body["items"]) == 2


async def test_list_users_invalid_limit_returns_400(client):
    resp = await client.get("/users", params={"limit": 0})
    assert resp.status_code == 400

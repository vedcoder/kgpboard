"""Tests for authentication (login + /auth/me)."""


async def _register(client, email="a@test.com", password="password1"):
    await client.post(
        "/users", json={"name": "A", "email": email, "password": password}
    )


async def test_login_success_returns_token(client):
    await _register(client)
    resp = await client.post(
        "/auth/login", data={"username": "a@test.com", "password": "password1"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["tokenType"] == "bearer"
    assert body["accessToken"]


async def test_login_wrong_password_returns_401(client):
    await _register(client)
    resp = await client.post(
        "/auth/login", data={"username": "a@test.com", "password": "WRONGPASS"}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect email or password."


async def test_login_unknown_email_same_message(client):
    # No user enumeration: unknown email yields the identical error.
    resp = await client.post(
        "/auth/login", data={"username": "nobody@test.com", "password": "whatever1"}
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Incorrect email or password."


async def test_me_returns_current_user(client, student_headers):
    resp = await client.get("/auth/me", headers=student_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "ravi@test.com"


async def test_me_without_token_returns_401(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_with_garbage_token_returns_401(client):
    resp = await client.get(
        "/auth/me", headers={"Authorization": "Bearer not.a.real.token"}
    )
    assert resp.status_code == 401

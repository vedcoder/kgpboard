"""Tests for notice creation (authz) and listing/filtering."""

NOTICE = {"title": "Exam schedule", "content": "midsem dates", "category": "Academic"}


async def test_admin_can_create_notice_with_nested_author(client, admin_headers):
    resp = await client.post("/notices", headers=admin_headers, json=NOTICE)
    assert resp.status_code == 201
    body = resp.json()
    # postedBy is the authenticated admin, embedded as a full User.
    assert body["postedBy"]["email"] == "admin@test.com"
    assert body["postedBy"]["role"] == "admin"
    assert "postedById" not in body


async def test_student_cannot_create_notice_403(client, student_headers):
    resp = await client.post("/notices", headers=student_headers, json=NOTICE)
    assert resp.status_code == 403


async def test_create_notice_without_token_401(client):
    resp = await client.post("/notices", json=NOTICE)
    assert resp.status_code == 401


async def test_create_notice_missing_field_400(client, admin_headers):
    resp = await client.post(
        "/notices", headers=admin_headers, json={"title": "only title"}
    )
    assert resp.status_code == 400
    fields = [e["field"] for e in resp.json()["errors"]]
    assert "content" in fields and "category" in fields


async def test_list_notices_filter_by_category(client, admin_headers):
    await client.post(
        "/notices", headers=admin_headers,
        json={"title": "A", "content": "x", "category": "Academic"},
    )
    await client.post(
        "/notices", headers=admin_headers,
        json={"title": "B", "content": "water cut", "category": "Hostel"},
    )
    resp = await client.get("/notices", params={"category": "Hostel"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "B"


async def test_list_notices_keyword_search(client, admin_headers):
    await client.post(
        "/notices", headers=admin_headers,
        json={"title": "Water supply", "content": "cut tomorrow", "category": "Hostel"},
    )
    await client.post(
        "/notices", headers=admin_headers,
        json={"title": "Exam", "content": "midsem", "category": "Academic"},
    )
    resp = await client.get("/notices", params={"q": "water"})
    assert resp.status_code == 200
    assert resp.json()["total"] == 1


async def test_list_notices_is_public(client, admin_headers):
    await client.post("/notices", headers=admin_headers, json=NOTICE)
    resp = await client.get("/notices")  # no auth header
    assert resp.status_code == 200
    assert resp.json()["total"] == 1

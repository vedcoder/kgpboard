"""Tests for event creation (authz + validation) and filtering/pagination."""


def event(**overrides) -> dict:
    """A valid event payload, with optional field overrides."""
    payload = {
        "title": "Tech Talk",
        "description": "AI at KGP",
        "category": "Talk",
        "venue": "Nalanda",
        "organizer": "Robotics Club",
        "startTime": "2026-08-01T10:00:00Z",
        "endTime": "2026-08-01T12:00:00Z",
    }
    payload.update(overrides)
    return payload


async def test_admin_can_create_event(client, admin_headers):
    resp = await client.post("/events", headers=admin_headers, json=event())
    assert resp.status_code == 201
    assert resp.json()["organizer"] == "Robotics Club"


async def test_create_event_with_poster_roundtrips(client, admin_headers):
    url = "https://example.com/poster.png"
    resp = await client.post("/events", headers=admin_headers, json=event(imageUrl=url))
    assert resp.status_code == 201
    assert resp.json()["imageUrl"] == url


async def test_get_event_by_id(client, admin_headers):
    created = await client.post("/events", headers=admin_headers, json=event())
    event_id = created.json()["id"]
    resp = await client.get(f"/events/{event_id}")  # no auth: reads are public
    assert resp.status_code == 200
    assert resp.json()["title"] == "Tech Talk"


async def test_get_missing_event_returns_404(client):
    resp = await client.get("/events/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_event_start_after_end_returns_400(client, admin_headers):
    resp = await client.post(
        "/events",
        headers=admin_headers,
        json=event(startTime="2026-08-01T12:00:00Z", endTime="2026-08-01T10:00:00Z"),
    )
    assert resp.status_code == 400
    assert resp.json()["detail"] == "startTime must be before endTime."


async def test_student_cannot_create_event_403(client, student_headers):
    resp = await client.post("/events", headers=student_headers, json=event())
    assert resp.status_code == 403


async def test_create_event_without_token_401(client):
    resp = await client.post("/events", json=event())
    assert resp.status_code == 401


async def test_event_missing_venue_returns_400(client, admin_headers):
    payload = event()
    del payload["venue"]
    resp = await client.post("/events", headers=admin_headers, json=payload)
    assert resp.status_code == 400
    assert "venue" in [e["field"] for e in resp.json()["errors"]]


async def _seed_events(client, admin_headers):
    await client.post(client_url := "/events", headers=admin_headers, json=event(
        title="TCS Placement", description="drive", category="Placement",
        startTime="2026-07-10T10:00:00Z", endTime="2026-07-10T12:00:00Z"))
    await client.post(client_url, headers=admin_headers, json=event(
        title="Robotics Workshop", description="line follower", category="Workshop",
        startTime="2026-08-05T10:00:00Z", endTime="2026-08-05T13:00:00Z"))
    await client.post(client_url, headers=admin_headers, json=event(
        title="Google Placement", description="SDE roles", category="Placement",
        startTime="2026-09-01T09:00:00Z", endTime="2026-09-01T11:00:00Z"))


async def test_list_events_filter_by_category(client, admin_headers):
    await _seed_events(client, admin_headers)
    resp = await client.get("/events", params={"category": "Placement"})
    assert resp.json()["total"] == 2


async def test_list_events_date_range_and_keyword(client, admin_headers):
    await _seed_events(client, admin_headers)
    resp = await client.get("/events", params={"from": "2026-08-01T00:00:00Z"})
    assert resp.json()["total"] == 2  # Robotics + Google
    resp = await client.get("/events", params={"q": "robot"})
    assert resp.json()["total"] == 1


async def test_list_events_pagination(client, admin_headers):
    await _seed_events(client, admin_headers)
    page1 = await client.get("/events", params={"limit": 2, "offset": 0})
    page2 = await client.get("/events", params={"limit": 2, "offset": 2})
    assert page1.json()["total"] == 3
    assert len(page1.json()["items"]) == 2
    assert len(page2.json()["items"]) == 1

# KGPBoard API

A REST API for campus **users**, **notices**, and **events** — built with FastAPI,
async SQLAlchemy 2.0, and PostgreSQL.

The codebase is organised in clear layers so responsibilities never blur:

```
HTTP request
   │
   ▼  app/api/routes/   ── thin endpoints: parse & validate (Pydantic), return
   ▼  app/services/     ── business rules, transaction boundary, domain errors
   ▼  app/repositories/ ── the ONLY code that touches SQL / ORM models
   ▼  app/models/       ── tables + DB constraints (unique, FK, CHECK)
PostgreSQL
```

- **Validation** happens at the edge (schemas) *and* the DB enforces it as the
  last line of defense.
- **Errors are informative** — every failure returns a JSON `detail` message,
  not just a status code.

---

## Tech stack

| Concern | Choice |
|---|---|
| Web framework | FastAPI |
| DB / driver | PostgreSQL 16 + asyncpg (async) |
| ORM / migrations | SQLAlchemy 2.0 (async) + Alembic |
| Auth | JWT (PyJWT, HS256) + Argon2 password hashing |
| Validation | Pydantic v2 |
| Rate limiting | SlowAPI |
| Tests | pytest + httpx |
| Packaging | uv, Docker + docker-compose |

---

## Running it

You can run **locally** (against your own Postgres) or **entirely in Docker**.
The two are independent and do not conflict — Docker publishes Postgres on host
port **5433**, local Postgres stays on **5432**.

### Option A — Docker (one command)

Requires only Docker.

```bash
docker compose up --build
```

This starts Postgres, waits for it to be healthy, applies migrations, and serves
the API at **http://localhost:8000** (docs at `/docs`). Create an admin:

```bash
docker compose exec api python scripts/create_admin.py "Asha" admin@kgp.ac.in adminpass123
```

### Option B — Local

Requires Python 3.14+, [uv](https://docs.astral.sh/uv/), and a running Postgres.

```bash
# 1. Install dependencies (creates .venv from uv.lock)
uv sync

# 2. Configure the database URL / secret
cp .env.example .env
#   edit .env: set DATABASE_URL and JWT_SECRET
#   generate a secret: python -c "import secrets; print(secrets.token_urlsafe(48))"

# 3. Create the database and apply migrations
createdb kgpboard
uv run alembic upgrade head

# 4. Run the API (auto-reload)
uv run uvicorn app.main:app --reload
```

Create an admin (public sign-up can only make students):

```bash
PYTHONPATH=. uv run python scripts/create_admin.py "Asha" admin@kgp.ac.in adminpass123
```

---

## Authentication

- **Register** (public) → always creates a `student`.
- **Log in** → receive a JWT access token.
- Send it as `Authorization: Bearer <token>` on protected requests.
- **Only admins** can create notices and events. Reads are public.

```bash
# register
curl -X POST localhost:8000/users -H 'Content-Type: application/json' \
  -d '{"name":"Ravi","email":"ravi@kgp.ac.in","password":"password1"}'

# log in (form fields; username = email) -> {"accessToken": "...", "tokenType": "bearer"}
curl -X POST localhost:8000/auth/login -d 'username=admin@kgp.ac.in&password=adminpass123'

# use the token
curl localhost:8000/auth/me -H "Authorization: Bearer <token>"
```

In `/docs`, use the **Authorize** button to log in and the token attaches
automatically.

---

## API reference

Base URL: `http://localhost:8000`. Interactive docs: `/docs`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | — | Exchange email + password for a token |
| GET | `/auth/me` | any user | The current authenticated user |
| POST | `/users` | — (public) | Register a new user (always a student) |
| GET | `/users` | — | List users (paginated) |
| POST | `/notices` | **admin** | Create a notice (author = you) |
| GET | `/notices` | — | List notices (filter + paginate) |
| POST | `/events` | **admin** | Create an event |
| GET | `/events` | — | List events (filter + paginate) |
| GET | `/health` | — | Liveness check |

Write endpoints (`POST /users`, `/notices`, `/events`) are **rate limited** to
`5/minute` per user (or per IP when anonymous); exceeding it returns `429`.

### Entities

- **User** — `id`, `name`, `email` (unique), `role` (`student` | `admin`), `createdAt`
- **Notice** — `id`, `title`, `content`, `category`, `postedBy` (full User), `createdAt`
- **Event** — `id`, `title`, `description`, `category`, `venue`, `startTime`, `endTime`, `organizer`, `createdAt`

### Filtering & pagination

List endpoints return a page envelope:

```json
{ "items": [ ... ], "total": 42, "limit": 20, "offset": 0 }
```

Query params:

- `limit` (1–100, default 20), `offset` (default 0) — all list endpoints
- `category` — exact match (`/notices`, `/events`)
- `from`, `to` — ISO-8601 range (events: on `startTime`; notices: on `createdAt`)
- `q` — keyword search (events: title/description; notices: title/content)

```bash
curl "localhost:8000/events?category=Placement&from=2026-07-01T00:00:00Z&limit=10"
```

### Example: create an event (admin)

```bash
curl -X POST localhost:8000/events \
  -H "Authorization: Bearer <admin-token>" -H 'Content-Type: application/json' \
  -d '{
        "title": "Tech Talk", "description": "AI at KGP", "category": "Talk",
        "venue": "Nalanda", "organizer": "Robotics Club",
        "startTime": "2026-08-01T10:00:00Z", "endTime": "2026-08-01T12:00:00Z"
      }'
```

### Error responses

Errors always carry a `detail` message. Validation errors also list each field:

```json
// 400 — missing/invalid fields
{ "detail": "Validation failed.", "errors": [ { "field": "email", "message": "value is not a valid email address" } ] }

// 409 — duplicate email
{ "detail": "A user with email 'asha@kgp.ac.in' already exists." }

// 400 — invalid date range
{ "detail": "startTime must be before endTime." }
```

| Status | When |
|---|---|
| 400 | Missing/invalid fields, bad date range, unknown reference |
| 401 | Missing/invalid token, or wrong login credentials |
| 403 | Authenticated but not an admin |
| 409 | Email already registered |
| 429 | Rate limit exceeded on a write endpoint |

---

## Tests

Runs against a throwaway `kgpboard_test` database (created and dropped
automatically); your dev data is never touched.

```bash
uv run pytest
```

---

## Project layout

```
app/
├── main.py            # FastAPI app: routers, error handlers, rate limiter
├── core/              # config, security (hashing/JWT), exceptions, ratelimit
├── db/                # async engine, session, declarative base
├── models/            # SQLAlchemy models + constraints
├── repositories/      # data access (SQL lives only here)
├── services/          # business logic + transactions
├── schemas/           # Pydantic request/response models
└── api/               # routes + dependencies (auth, session)
alembic/               # migrations
scripts/create_admin.py
tests/
Dockerfile · docker-compose.yml
```

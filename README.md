# KGPBoard

A full-stack **campus notices & events** platform:

- **Backend** — a REST API (FastAPI + async SQLAlchemy + PostgreSQL).
- **Web** — a responsive React dashboard where students browse notices and
  events, and admins post them.

> **Live demo:** **https://kgpboard.vercel.app**
>
> - **Frontend** → Vercel · **API** → Render (Docker) · **Database** → Render Postgres.
> - The free API **sleeps when idle**, so the first request may take ~30–60s to wake.
> - Admin login: `asha@kgp.ac.in` / `adminpass123`.
>
> ⚠️ **Free-tier caveats (this deployment):**
> - The free **Render Postgres is deleted ~30 days after creation** (created
>   2026-07-05 → expires early August 2026); after that the live demo's data goes.
> - **Render maintenance window:** July 8th, 06:30 IST (July 8th, 01:00 UTC) —
>   the app may be briefly unavailable around then.
> - Uploaded posters are **ephemeral** on the free tier (no persistent disk), so
>   newly uploaded images may disappear on redeploy; seeded posters still show.

```
web/   → React + Vite + TypeScript frontend
app/   → FastAPI backend
```

The two talk over HTTP; the frontend's data layer (`web/src/api`, `web/src/hooks`)
is deliberately free of DOM code so a future mobile app could reuse it.

---

## Features

**Web dashboard**
- Notice & event feeds as responsive cards (poster thumbnail, or a placeholder).
- Detail pages, deep-linkable (`/notices/:id`, `/events/:id`).
- Keyword search **and** category filter, together, stored in the URL.
- "Load more" pagination, loading/error/empty states, dark mode (remembered).
- Auth: sign up (with inline field validation) / log in; admins get a **＋ New**
  form to post notices/events with **drag-drop poster upload**.
- Admin **user management** page: search users by email and change their role.

**Backend API**
- Users, notices, events with full validation and informative JSON errors.
- JWT auth + role-based access (only admins write), Argon2 password hashing.
- Filtering, pagination, fixed category enums, image uploads, rate limiting.
- 33 tests, Dockerised, Alembic migrations.

---

## Backend

Organised in clear layers so responsibilities never blur:

```
HTTP request
   ▼  app/api/routes/   ── thin endpoints: parse & validate (Pydantic)
   ▼  app/services/     ── business rules, transactions, domain errors
   ▼  app/repositories/ ── the ONLY code that touches SQL / ORM models
   ▼  app/models/       ── tables + DB constraints (unique, FK, CHECK, enums)
PostgreSQL
```

### Tech stack

| Concern | Choice |
|---|---|
| Framework | FastAPI |
| DB / driver | PostgreSQL 16 + asyncpg (async) |
| ORM / migrations | SQLAlchemy 2.0 (async) + Alembic |
| Auth | JWT (PyJWT, HS256) + Argon2 (pwdlib) |
| Validation | Pydantic v2 |
| Rate limiting | SlowAPI |
| Tests | pytest + httpx |
| Packaging | uv, Docker + docker-compose |

### Running the backend

**Option A — Docker (one command):**

```bash
docker compose up --build
```

Starts Postgres, applies migrations, serves the API at **http://localhost:8000**
(docs at `/docs`). Create an admin:

```bash
docker compose exec api python scripts/create_admin.py "Asha" admin@kgp.ac.in adminpass123
```

**Option B — Local** (Python 3.14+, [uv](https://docs.astral.sh/uv/), local Postgres):

```bash
uv sync                                  # install deps from uv.lock
cp .env.example .env                     # set DATABASE_URL and JWT_SECRET
createdb kgpboard
uv run alembic upgrade head                        # create tables
PYTHONPATH=. uv run python scripts/seed_demo.py    # optional: demo data + 2 admins
uv run uvicorn app.main:app --reload
```

`scripts/seed_demo.py` creates demo content and two admins
(`asha@kgp.ac.in`, `rahul@kgp.ac.in`, password `adminpass123`).

> Local Postgres (`:5432`) and the Docker one (`:5433`) are independent and
> don't conflict — run either.

### API reference

Base URL `http://localhost:8000`, interactive docs at `/docs`.

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/login` | — | Exchange email + password for a token |
| GET | `/auth/me` | user | The current authenticated user |
| POST | `/users` | — | Register (public; always a student) |
| GET | `/users` | **admin** | List/search users by email (paginated) |
| PATCH | `/users/{id}/role` | **admin** | Change a user's role (not your own) |
| GET/POST | `/notices` | read: — / write: **admin** | List / create notices |
| GET | `/notices/{id}` | — | A single notice |
| GET/POST | `/events` | read: — / write: **admin** | List / create events |
| GET | `/events/{id}` | — | A single event |
| POST | `/uploads` | **admin** | Upload a poster image → `{ "url": … }` |
| GET | `/meta` | — | Allowed category & target-year values |
| GET | `/health` | — | Liveness check |

Write endpoints are **rate limited** to `5/minute` (→ `429`).

### Entities

- **User** — `id`, `name`, `email` (unique), `role` (`student`|`admin`), `createdAt`
- **Notice** — `id`, `title`, `content`, `category`, `postedBy` (full User), `imageUrl?`, `createdAt`
- **Event** — `id`, `title`, `description`, `category`, `venue`, `startTime`, `endTime`, `organizer`, `imageUrl?`, `registrationUrl?`, `targetYear?`, `createdAt`

**Categories are fixed enums** (invalid values → `400` with the list of options):
- Notices: `Academic, Examination, Placement, Hostel, Scholarship, General`
- Events: `Workshop, Talk, Cultural, Sports, Placement, Fest`
- Target year: `All years, 1st year … 5th year`

### Filtering & pagination

List endpoints return `{ items, total, limit, offset }`. Query params:
`limit` (1–100), `offset`, `category`, `from`/`to` (ISO-8601 range), `q` (keyword).

```bash
curl "localhost:8000/events?category=Placement&from=2026-07-01T00:00:00Z&limit=10"
```

### Errors

| Status | When |
|---|---|
| 400 | Missing/invalid fields, bad date range, invalid category |
| 401 | Missing/invalid token, or wrong login |
| 403 | Authenticated but not an admin |
| 404 | Notice/event not found |
| 409 | Email already registered |
| 429 | Rate limit exceeded |

```json
{ "detail": "Validation failed.", "errors": [ { "field": "email", "message": "…" } ] }
```

### Tests

```bash
uv run pytest    # runs against a throwaway kgpboard_test DB
```

---

## Web

React + Vite + TypeScript, TanStack Query for data, React Router, plain CSS.

```bash
cd web
npm install
npm run dev        # http://localhost:5173
```

By default it calls the API at `http://localhost:8000`. To point elsewhere, set
`VITE_API_URL` (see `web/.env.example`). Make sure the backend's `CORS_ORIGINS`
allows the frontend origin.

```
web/src/
├── types.ts        # shared API types            ┐ portable (no DOM) — a
├── api/client.ts   # typed fetch client          │ React Native app could
├── hooks/          # TanStack Query hooks         ┘ reuse this layer
├── components/     # header, cards, feeds, states
├── pages/          # dashboard, detail, login, signup, create
├── auth/           # AuthProvider (token persistence)
└── theme/          # dark mode
```

---

## Deployment

**This project is deployed as:** frontend on **Vercel**, and the **API +
Postgres on Render** (provisioned together from [`render.yaml`](render.yaml) —
Render → New → Blueprint → this repo). The steps below generalise that setup.

Recommended split: **frontend on Vercel**, **backend + Postgres on a host that
runs a long-lived server** (Render, Railway, or Fly.io). Vercel is ideal for the
static React app but not for our persistent async Python server.

**1. Database (managed Postgres).** Create one on your backend host, or use
Vercel Postgres / Neon / Supabase. You'll get a connection string. Convert it for
async SQLAlchemy by using the `postgresql+asyncpg://` scheme, and pass SSL via
`connect_args` (managed Postgres requires SSL; asyncpg does **not** accept
`?sslmode=` in the URL):

```
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME?ssl=require
```

Run migrations against it once: `DATABASE_URL=… uv run alembic upgrade head`.

**2. Backend (Render/Railway/Fly).** Deploy this repo; set env vars
`DATABASE_URL`, `JWT_SECRET`, and `CORS_ORIGINS=https://your-frontend.vercel.app`.
Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
Note: poster uploads use local disk by default, which is **ephemeral** on most
hosts — switch `app/core/storage.py` to S3/Cloudflare R2 for persistent uploads
(the storage class is the only thing that changes).

**3. Frontend (Vercel).** Import the repo, set **Root Directory** to `web`,
framework **Vite** (build `npm run build`, output `dist`). Add an env var
`VITE_API_URL=https://your-backend-host`. Add an SPA rewrite so client-side
routes (`/events/:id`) don't 404 on refresh — create `web/vercel.json`:

```json
{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }
```

Then put the live URL at the top of this README.

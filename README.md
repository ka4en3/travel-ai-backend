# Travel-AI Backend

A FastAPI-based backend for generating, storing, and sharing travel itineraries via AI and caching.  
Supports both JWT-protected REST endpoints and Telegram-bot authentication.

OTUS Python Basic Thesis Project.

---

## 🚀 Features

- **User registration & authentication**  
  - Email + password registration and Telegram user registration (`/auth/register`) 
  - OAuth2 password-grant login returning JWT (`/auth/login`) 
  - `get_current_user` dependency to protect REST endpoints  

- **AI-powered route generation**  
  - `/routes/` POST generates a new itinerary  
    1. Look up similar params in `AICache`  
    2. On cache miss → call AI API (not implement yet)  
    3. Persist new `AICache` entry  
    4. Persist new `Route`, `RouteDay`, `Activity` records  
  - Shareable `share_code` (NanoID)  

- **Route CRUD & share → access control**  
  - GET/PUT/DELETE `/routes/{id}` with fine-grained role checks  
    - Viewer, Editor, Creator roles via `RouteAccess` ACL table  
    - `require_route_access([...])` dependency  
  - Invite by share code:  
    - GET `/route-access/{route_id}/get-share-code`  
    - POST `/route-access/accept-by-code`  
    - POST `/route-access/{route_id}/grant-editor`  
    - DELETE `/route-access/{route_id}/revoke-access`  

- **Database & migrations**  
  - PostgreSQL + Alembic migrations  
  - SQLAlchemy 2.0 async ORM with Pydantic models  

- **Testing**  
  - Pytest + pytest-asyncio  
  - In-memory SQLite for fast integration tests  
  - Fixtures seed full data: users, cache entries, routes, access  

---

## ❌ Not Yet Implemented

- AI API integration
- Redis for intermediate AI prompt caching
- Pagination on list endpoints  
- Webhook endpoints (you will hook your Telegram bot to `/webhook/...`)  
- Google Calendar / Docs export (stubbed `Export` model only)  
- Fine-grained “last_edited_by” tracking on routes  
- Rate-limiting / abuse protection  

---

## 🛠️ Getting Started

### 1. Clone & Install

```bash
git clone https://github.com/ka4en3/travel-ai-backend.git
cd travel-ai-backend
python -m venv .venv
source .venv/bin/activate  # или .venv\Scripts\activate  (Windows)
pip install -r requirements.txt
```

### 2. Environment

Copy `.env.example` to `.env` and fill in:

```ini
# PostgreSQL
POSTGRES_USER=admin
POSTGRES_PASSWORD=password
POSTGRES_DB=travel_ai_db
DB_HOST=localhost

# Redis
REDIS_URL=redis://localhost:6379/0

# Telegram (bot API)
TELEGRAM_TOKEN=your_telegram_token

# OpenAI / ChatGPT
CHATGPT_API_KEY=your_chatgpt_api_key

# JWT settings
JWT_SECRET_KEY=supersecret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# FastAPI
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Database & Migrations

Make sure PostgreSQL are running, then:

```bash
# generate an Alembic revision (if you’ve changed models)
alembic revision --autogenerate -m "My change"

# apply migrations
alembic upgrade head
```

### 4. Seed Data (Optional)

To load fixture data:

```bash
python app/fixtures/load_with_services.py
```

This will create:
- 10 test users (with telegram_id or e-mail)
- 5 AI-cache entries
- 5 auto-generated routes
- Additional route-access grants

### 5. Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit the interactive docs at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 🧪 Testing

All tests use an **in-memory SQLite** and seed data via `fixtures/load_with_services.py`.  

```bash
pytest
```

**Coverage highlights**:
- **Auth** (`test_auth.py`): register, duplicate-register, login success/failure
- **Routes** (`test_routes.py`):  
  - unauthorized checks  
  - create, get by ID, list, get by share_code  
  - rebuild, delete, owner filters  
- **Route-Access ACL** (`test_route_access.py`):  
  - share-code invite flow  
  - grant editor, revoke  
  - permission checks for every role  

---

## 🎯 Next Steps

1. **AI API**: integrate route building by promting of proper AI (ChatGPT, Gemini)
2. **Redis**: introduce Redis for intermediate AI prompt caching (quick cache)
3. **Webhook**: expose `/webhook/telegram` and wire to your bot  
4. **Exports**: implement Google Calendar & PDF exports  
5. **Pagination**: add `limit`/`offset` to listing endpoints  
6. **Monitoring & Metrics**: request tracing, Redis hit ratio, errors  
7. **Rate-Limiting**: protect AI calls and public routes  
8. **Production Hardening**: dockerize, k8s manifests, secrets management  

---

## 📄 License

MIT License © ka4en3

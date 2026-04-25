# 🏓 PingRoom — Real-time Chat SaaS Backend

Production-ready FastAPI backend for a real-time chat application with Supabase Auth, PostgreSQL, and Stripe payments.

---

## 📁 Project Structure

```
pingroom/
├── main.py                         # FastAPI app entry point
├── requirements.txt
├── Dockerfile
├── .env.example                    # Environment variable template
├── supabase_schema.sql             # Database schema + RLS policies
└── app/
    ├── core/
    │   ├── config.py               # Pydantic settings (reads .env)
    │   ├── logging.py              # Structured logging setup
    │   ├── supabase.py             # Supabase client factory
    │   └── stripe_client.py        # Stripe client initialisation
    ├── middleware/
    │   └── auth.py                 # JWT validation dependency
    ├── models/
    │   └── schemas.py              # Pydantic request/response schemas
    ├── services/
    │   ├── auth_service.py         # Supabase Auth operations
    │   ├── room_service.py         # Chat room CRUD
    │   ├── message_service.py      # Message send/fetch with pagination
    │   ├── sticker_service.py      # Sticker catalogue + purchases
    │   └── payment_service.py      # Stripe checkout + purchase recording
    └── routes/
        ├── auth.py                 # POST /api/v1/auth/...
        ├── rooms.py                # GET|POST|DELETE /api/v1/rooms/...
        ├── messages.py             # POST|GET /api/v1/messages/...
        ├── stickers.py             # GET|POST /api/v1/stickers/...
        ├── payments.py             # POST /api/v1/payments/checkout
        └── webhooks.py             # POST /api/v1/webhooks/stripe
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-org/pingroom.git
cd pingroom

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Supabase and Stripe credentials
```

### 3. Set Up Supabase Database

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and paste + run `supabase_schema.sql`
3. Copy your credentials from **Project Settings → API**

### 4. Set Up Stripe

1. Create an account at [stripe.com](https://stripe.com)
2. Copy API keys from **Developers → API Keys**
3. For webhooks (local dev): install the [Stripe CLI](https://stripe.com/docs/stripe-cli)

```bash
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
# Copy the "whsec_..." signing secret into .env → STRIPE_WEBHOOK_SECRET
```

### 5. Run the Server

```bash
uvicorn main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for the interactive API docs.

---

## 🌐 API Reference

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/signup` | ❌ | Register a new user |
| `POST` | `/api/v1/auth/signin` | ❌ | Sign in, receive JWT |
| `POST` | `/api/v1/auth/signout` | ✅ | Invalidate session |
| `GET`  | `/api/v1/auth/me` | ✅ | Get current user info |

### Rooms

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET`    | `/api/v1/rooms/` | ✅ | List all rooms |
| `POST`   | `/api/v1/rooms/` | ✅ | Create a room |
| `GET`    | `/api/v1/rooms/{room_id}` | ✅ | Get room details |
| `DELETE` | `/api/v1/rooms/{room_id}` | ✅ | Delete room (creator only) |

### Messages

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST`   | `/api/v1/messages/` | ✅ | Send a message to a room |
| `GET`    | `/api/v1/messages/room/{room_id}?page=1&page_size=50` | ✅ | Fetch paginated messages |
| `DELETE` | `/api/v1/messages/{message_id}` | ✅ | Delete your message |

### Stickers

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET`  | `/api/v1/stickers/` | ✅ | Browse sticker catalogue |
| `GET`  | `/api/v1/stickers/my-stickers` | ✅ | Your purchased stickers |
| `POST` | `/api/v1/stickers/` | ✅ | Add sticker (admin) |

### Payments

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/payments/checkout` | ✅ | Create Stripe checkout session |
| `GET`  | `/api/v1/payments/verify/{sticker_id}` | ✅ | Check if you own a sticker |
| `POST` | `/api/v1/webhooks/stripe` | ❌ | Stripe webhook (signature-verified) |

---

## 🔐 Authentication Flow

All protected routes require a `Bearer` token in the `Authorization` header:

```
Authorization: Bearer <supabase_access_token>
```

1. Client calls `POST /api/v1/auth/signin` → receives `access_token`
2. Client attaches token to every subsequent request
3. Backend validates JWT signature using `SUPABASE_JWT_SECRET`
4. `CurrentUser` dependency injects `user_id`, `email`, `role` into route handlers

---

## 💳 Stripe Payment Flow

```
Client                     PingRoom API               Stripe
  │                             │                         │
  ├─ POST /payments/checkout ──►│                         │
  │                             ├─ Create Session ───────►│
  │                             │◄── session.url ─────────┤
  │◄── { checkout_url } ────────┤                         │
  │                             │                         │
  ├─ Redirect to checkout_url ─────────────────────────►  │
  │                        (User pays on Stripe)           │
  │◄──────────────────── Redirect to success_url ──────── │
  │                             │                         │
  │              POST /webhooks/stripe ◄───────────────── │
  │                             │  (checkout.session.completed)
  │                             ├─ Verify signature        │
  │                             ├─ Record purchase in DB   │
  │                             └─ 200 OK ────────────────►│
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t pingroom:latest .

# Run container
docker run -d \
  --name pingroom \
  -p 8000:8000 \
  --env-file .env \
  pingroom:latest
```

### Docker Compose (with Nginx)

```yaml
version: "3.9"
services:
  api:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## ☁️ Production Deployment

### Railway / Render / Fly.io

1. Push to GitHub
2. Connect repo to your platform
3. Set all environment variables from `.env.example`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Production Checklist

- [ ] `ENVIRONMENT=production` (disables `/docs` and `/redoc`)
- [ ] Strong random `SECRET_KEY`
- [ ] `ALLOWED_ORIGINS` set to your actual frontend domain(s)
- [ ] Stripe live keys (`sk_live_...`, `pk_live_...`)
- [ ] Stripe webhook registered for your production URL
- [ ] Supabase RLS policies enabled and tested
- [ ] HTTPS enforced (handled by platform/load balancer)

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

Example test with auth:

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_list_rooms_requires_auth():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/rooms/")
    assert response.status_code == 403
```

---

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `supabase` | Supabase Python client (Auth + DB) |
| `stripe` | Stripe payment integration |
| `PyJWT` | JWT validation |
| `pydantic-settings` | Typed env var configuration |

---

## 📝 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | ✅ | Your Supabase project URL |
| `SUPABASE_ANON_KEY` | ✅ | Public anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Secret service-role key |
| `SUPABASE_JWT_SECRET` | ✅ | JWT signing secret |
| `STRIPE_SECRET_KEY` | ✅ | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | ✅ | Stripe public key |
| `STRIPE_WEBHOOK_SECRET` | ✅ | Stripe webhook signing secret |
| `FRONTEND_URL` | ✅ | Frontend origin for redirects |
| `ALLOWED_ORIGINS` | ✅ | CORS origins (JSON array) |
| `ENVIRONMENT` | ❌ | `development` (default) or `production` |

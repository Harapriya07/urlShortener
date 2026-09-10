# TrimURL

A full-stack URL shortener built with **FastAPI, PostgreSQL, Redis, and React**.

TrimURL converts long URLs into compact short codes and provides fast redirects, Redis-based caching, rate limiting, and click analytics.

## Features

* Shorten long URLs into compact Base62 short codes
* Return the same short code for duplicate URLs
* Fast URL redirects using Redis caching
* PostgreSQL persistence
* Redis-based rate limiting
* Redis-based click tracking
* Daily click analytics
* Background synchronization of Redis click counts to PostgreSQL
* Atomic click synchronization using Redis Lua scripting
* Database schema migrations using Alembic
* Automated backend tests with pytest
* Responsive React frontend
* Environment-based configuration

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Redis
* Alembic
* Pytest

### Frontend

* React
* Vite
* JavaScript
* CSS

## Architecture

```text
                    ┌───────────────┐
                    │ React Frontend│
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    FastAPI    │
                    └───┬───────┬───┘
                        │       │
              ┌─────────┘       └─────────┐
              ▼                           ▼
       ┌─────────────┐             ┌─────────────┐
       │ PostgreSQL  │             │    Redis    │
       │             │             │             │
       │ URLs        │             │ URL Cache   │
       │ Clicks      │             │ Rate Limit  │
       │ Metadata    │             │ Clicks      │
       └─────────────┘             └──────┬──────┘
                                          │
                                          ▼
                                  Background Worker
                                          │
                                          ▼
                                     PostgreSQL
```

## How URL Shortening Works

When a user submits a URL:

1. FastAPI receives the request.
2. The rate limiter checks whether the client has exceeded its request limit.
3. PostgreSQL is checked for an existing copy of the URL.
4. If the URL already exists, its existing short code is returned.
5. Otherwise, a new database record is created.
6. The database-generated ID is converted into a Base62 short code.
7. The short code is stored with the URL.
8. The short code is returned to the frontend.

### Base62 Encoding

TrimURL uses the following character set:

```text
0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
```

A database ID is converted into a compact Base62 representation.

For example:

```text
62  → 10
63  → 11
104 → 1G
105 → 1H
```

This avoids generating long random strings while producing compact, URL-friendly identifiers.

## Redis Caching

When a short URL is accessed:

```text
User
  │
  ▼
FastAPI
  │
  ├── Redis cache hit ──► Redirect
  │
  └── Cache miss
          │
          ▼
      PostgreSQL
          │
          ▼
      Store in Redis
          │
          ▼
        Redirect
```

Cached URLs have a **1-hour TTL**.

Redis reduces repeated database lookups for frequently accessed short URLs.

## Rate Limiting

The `/shorten` endpoint uses a Redis-based token bucket rate limiter.

Each client is associated with a Redis token bucket.

When the available tokens are exhausted, the API returns:

```text
429 Too Many Requests
```

This helps protect the API from excessive requests and basic abuse.

## Click Tracking

Clicks are initially recorded in Redis rather than immediately updating PostgreSQL.

For a short code such as `1T`:

```text
clicks:1T
```

stores pending total clicks.

Daily analytics are stored using keys such as:

```text
daily_clicks:1T:2026-09-09
```

This allows click information to be recorded quickly without performing a database write for every redirect.

## Background Click Synchronization

A background worker runs periodically and synchronizes pending Redis click counts into PostgreSQL.

```text
Redirect
   │
   ▼
Redis
   │
   │ click count
   ▼
Background Worker
   │
   ▼
PostgreSQL
```

The worker runs every **30 seconds**.

This creates eventual consistency between Redis and the PostgreSQL `clicks` column while keeping redirects lightweight.

### Atomic Synchronization

Redis Lua scripting is used during synchronization.

The script:

1. Reads the current Redis click count.
2. Resets the Redis counter atomically.
3. Returns the number of clicks that were captured.
4. The worker adds those clicks to PostgreSQL.
5. If the database update fails, the clicks are restored to Redis.

This reduces the risk of losing clicks during synchronization.

## Analytics

TrimURL provides an analytics endpoint:

```text
GET /analytics/{short_code}
```

It returns:

* Short code
* Original URL
* Total persisted clicks
* Today's clicks
* Click counts for the previous 7 days
* Creation timestamp

Today's click count is read directly from Redis, allowing recent activity to be reflected without waiting for the background synchronization.

## Database Migrations

TrimURL uses **Alembic** for database schema migrations.

Create a migration:

```bash
alembic revision --autogenerate -m "migration message"
```

Apply migrations:

```bash
alembic upgrade head
```

Check for schema differences:

```bash
alembic check
```

## Testing

The backend uses **pytest** with a separate test database and Redis cleanup between tests.

The test suite covers:

* Base62 encoding
* URL shortening
* Duplicate URL handling
* Different URL handling
* Invalid URLs
* Redirects
* Missing short URLs
* Click counting
* Multiple clicks
* Rate limiting
* Analytics
* Analytics after clicks

Run the tests with:

```bash
pytest
```

## Project Structure

```text
urlShortner/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── redis_client.py
│   └── rate_limiter.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── tests/
│   ├── conftest.py
│   ├── test_base62.py
│   └── test_shorten.py
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd urlShortner
```

### 2. Create and activate the Python virtual environment

Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file based on:

```text
.env.example
```

Configure:

```text
DATABASE_URL
REDIS_HOST
REDIS_PORT
FRONTEND_URL
TEST_DATABASE_URL
```

Never commit the actual `.env` file.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start Redis

Make sure your Redis server is running.

### 7. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

The API will be available locally at:

```text
http://localhost:8000
```

FastAPI's interactive API documentation:

```text
http://localhost:8000/docs
```

### 8. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The React application will be available at the Vite development address shown in the terminal.

## API Endpoints

| Method | Endpoint                  | Purpose                        |
| ------ | ------------------------- | ------------------------------ |
| POST   | `/shorten`                | Create or retrieve a short URL |
| GET    | `/{short_code}`           | Redirect to the original URL   |
| GET    | `/analytics/{short_code}` | Retrieve click analytics       |

## Future Improvements

Potential future improvements include:

* User accounts and authentication
* Custom aliases
* URL expiration
* QR code generation
* More detailed analytics
* Redis distributed rate limiting improvements
* Background task processing using a dedicated worker system
* Production deployment with separate backend, frontend, database, and Redis services

## Author

Built as a full-stack backend-focused project to explore **API development, caching, rate limiting, database design, background processing, and system design concepts**.

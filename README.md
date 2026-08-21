# Vetty Crypto Market API

A Flask REST API that serves cryptocurrency market data from CoinGecko. Features include JWT authentication, in-memory caching with TTL, structured JSON logging, request ID middleware, and optional webhook notifications on market data fetches.

---

## Tech Stack

- **Python 3.13**
- **Flask** — web framework
- **Flask-JWT-Extended** — JWT authentication
- **Flasgger** — Swagger/OpenAPI documentation
- **httpx** — async HTTP client for CoinGecko calls
- **cachetools** — TTLCache for in-memory caching
- **python-json-logger** — structured JSON logging
- **python-dotenv** — environment variable loading

---

## Project Structure

```
vetty_project/
├── app/
│   ├── __init__.py          # App factory (create_app)
│   ├── config.py            # Environment-based config
│   ├── errors.py            # Custom exceptions + error handlers
│   ├── extensions.py        # JWT, cache singletons
│   ├── logging_config.py    # Structured JSON logging
│   ├── middleware.py        # Request ID + access logging
│   ├── blueprints/
│   │   ├── auth.py          # POST /auth/login
│   │   ├── categories.py    # GET /categories
│   │   ├── coins.py         # GET /coins
│   │   ├── health.py        # GET /health
│   │   └── market.py        # GET /market
│   ├── services/
│   │   ├── coingecko.py     # Async CoinGecko API client
│   │   └── webhook.py       # Webhook notification service
│   └── utils/
│       └── pagination.py    # Pagination helpers
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_cache.py
│   ├── test_categories.py
│   ├── test_coins.py
│   ├── test_health.py
│   ├── test_market.py
│   └── test_webhook.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── run.py
```

---

## Environment Variables

| Variable | Description | Required | Default |
|---|---|---|---|
| `JWT_SECRET_KEY` | Secret key for signing JWTs | Yes | — |
| `API_USERNAME` | Login username | Yes | — |
| `API_PASSWORD` | Login password | Yes | — |
| `APP_VERSION` | Application version string | No | `1.0.0` |
| `COINGECKO_BASE_URL` | CoinGecko API base URL | No | `https://api.coingecko.com/api/v3` |
| `COINGECKO_TIMEOUT_SECONDS` | HTTP timeout for CoinGecko calls | No | `10` |
| `CACHE_TTL_SECONDS` | In-memory cache TTL in seconds | No | `60` |
| `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` | JWT token lifetime in minutes | No | `60` |
| `WEBHOOK_URL` | URL to POST market fetch notifications | No | `""` (disabled) |
| `WEBHOOK_TIMEOUT_SECONDS` | Timeout for webhook POST requests | No | `10` |
| `LOG_LEVEL` | Python log level | No | `INFO` |

---

## Getting Started — Local Setup

```bash
# Clone the repo
git clone <repo-url>
cd vetty_project

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env and fill in JWT_SECRET_KEY, API_USERNAME, API_PASSWORD

# Run the server
python run.py
```

Server runs at http://localhost:8000

---

## Getting Started — Docker

```bash
cp .env.example .env
# Edit .env and fill in JWT_SECRET_KEY, API_USERNAME, API_PASSWORD

docker compose up --build
```

Server runs at http://localhost:8000

---

## API Documentation

Swagger UI is available at **http://localhost:8000/apidocs** once the server is running. All endpoints are documented with request/response schemas.

---

## Authentication

All endpoints except `/health` require a valid JWT token.

1. POST to `/auth/login` with your credentials:

```json
{
  "username": "your-username",
  "password": "your-password"
}
```

2. Use the returned token in subsequent requests:

```
Authorization: Bearer <token>
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/health` | No | App health status + CoinGecko reachability |
| POST | `/auth/login` | No | Get JWT access token |
| GET | `/coins` | Yes | Paginated list of all coins |
| GET | `/categories` | Yes | Paginated list of all categories |
| GET | `/market` | Yes | Market data in CAD (`coin_id` and/or `category` required) |

---

## Pagination

All list endpoints support `?page_num=1&per_page=10` (defaults). Maximum `per_page` is 250.

Response shape:

```json
{
  "data": [...],
  "pagination": {
    "page_num": 1,
    "per_page": 10,
    "total_items": 18500
  }
}
```

---

## Error Responses

All errors return a consistent JSON structure:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "At least one of 'coin_id' or 'category' must be provided.",
  "request_id": "a1b2c3d4-..."
}
```

Common error codes:

| Code | HTTP Status | Meaning |
|---|---|---|
| `VALIDATION_ERROR` | 400 | Invalid or missing request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid JWT token |
| `NOT_FOUND` | 404 | Resource not found |
| `UPSTREAM_ERROR` | 502 | CoinGecko returned an error |
| `GATEWAY_TIMEOUT` | 504 | CoinGecko request timed out |

---

## Running Tests

```bash
pytest tests/ --cov=app --cov-report=term-missing -v
```

Coverage: 87%

---

## Linting

```bash
ruff check app/ tests/
black --check app/ tests/
```

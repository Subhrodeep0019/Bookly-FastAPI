# Bookly

Bookly is an asynchronous FastAPI REST API for a book-review service. It provides JWT-based authentication, role-protected book and review endpoints, Redis-backed logout, account verification, password-reset emails, and Alembic-managed PostgreSQL migrations.

## Features

- User registration, login, account verification, and password reset
- JWT access and refresh tokens
- Redis blocklisting for logged-out access tokens
- Role-based protection for book and review resources
- Create, read, update, and delete books
- Create reviews and retrieve the current user's books or reviews
- Email delivery through FastAPI-Mail and Celery
- Async PostgreSQL access using SQLModel and `asyncpg`
- Alembic migrations, request logging middleware, and centralized error handling
- Pytest coverage for book routes

## Tech stack

- Python 3.14+
- FastAPI, Uvicorn, and Pydantic Settings
- SQLModel, SQLAlchemy async, PostgreSQL, and `asyncpg`
- Alembic
- Redis
- PyJWT and `pwdlib[argon2]`
- FastAPI-Mail, Celery, and Flower
- uv and pytest

## Project structure

```text
Bookly/
├── src/
│   ├── __init__.py              # FastAPI application and router setup
│   ├── config.py                # Environment-based application, Redis, and mail settings
│   ├── celery_task.py           # Celery task for asynchronous email delivery
│   ├── mail.py                  # FastAPI-Mail configuration and message factory
│   ├── middleware.py            # Custom HTTP request logging middleware
│   ├── errors.py                # Application exceptions and error handlers
│   ├── auth/
│   │   ├── dependencies.py      # JWT, current-user, and role dependencies
│   │   ├── routes.py            # Authentication, verification, and reset routes
│   │   ├── schemas.py           # User and authentication schemas
│   │   ├── service.py           # User persistence operations
│   │   └── utils.py             # Password and token utilities
│   ├── books/
│   │   ├── book_routes.py       # Book endpoints
│   │   ├── schemas.py           # Book request and response schemas
│   │   └── service.py           # Book persistence operations
│   ├── reviews/
│   │   ├── routes.py            # Review endpoints
│   │   ├── schemas.py           # Review request and response schemas
│   │   └── service.py           # Review persistence operations
│   ├── db/
│   │   ├── main.py              # Async database engine and session dependency
│   │   ├── model.py             # User, book, and review SQLModel tables
│   │   └── redis_client.py      # Redis token-blocklist helpers
│   ├── templates/
│   │   ├── email_verification.html
│   │   └── password_reset.html
│   └── tests/
│       ├── conftest.py          # Dependency overrides and shared test fixtures
│       └── test_book.py         # Book-route tests
├── migration_fol/
│   ├── env.py                   # Alembic async migration environment
│   ├── script.py.mako
│   └── versions/                # Database migration revisions
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── README.md
```

## Setup

Install the locked project dependencies:

```bash
uv sync
```

Create a `.env` file at the project root:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/bookly
JWT_SECRET=replace_with_a_secure_secret
JWT_ALGORITHM=HS256
REDIS_URL=redis://localhost:6379

MAIL_USERNAME=your_mail_username
MAIL_PASSWORD=your_mail_password
MAIL_FROM=your_email@example.com
MAIL_FROM_NAME=Bookly
MAIL_PORT=465
MAIL_SERVER=smtp.example.com
MAIL_STARTTLS=false
MAIL_SSL_TLS=true
USE_CREDENTIALS=true
VALIDATE_CERTS=true

DOMAIN=127.0.0.1:8000
```

Start PostgreSQL and Redis, then apply the migrations:

```bash
uv run alembic upgrade head
```

Start the API:

```bash
uv run uvicorn src:app --reload
```

The API and interactive OpenAPI documentation are available at `http://127.0.0.1:8000` and `http://127.0.0.1:8000/docs`.

## Background email worker

Account-verification and password-reset messages are queued through Celery, using Redis as both the broker and result backend. Run a worker alongside the API:

```bash
uv run celery -A src.celery_task.c_app worker --loglevel=info
```

Optionally monitor Celery tasks with Flower:

```bash
uv run celery -A src.celery_task.c_app flower
```

## Environment variables

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | Async PostgreSQL connection URL. |
| `JWT_SECRET` | Secret used to sign JWTs. |
| `JWT_ALGORITHM` | JWT signing algorithm, such as `HS256`. |
| `REDIS_URL` | Redis URL used for the token blocklist and Celery. |
| `MAIL_USERNAME` | SMTP account username. |
| `MAIL_PASSWORD` | SMTP account password or app password. |
| `MAIL_FROM` | Sender email address. |
| `MAIL_FROM_NAME` | Display name for outgoing mail. |
| `MAIL_PORT` | SMTP server port. |
| `MAIL_SERVER` | SMTP server hostname. |
| `MAIL_STARTTLS` | Enables STARTTLS for the SMTP connection. |
| `MAIL_SSL_TLS` | Enables SSL/TLS for the SMTP connection. |
| `USE_CREDENTIALS` | Enables SMTP authentication. |
| `VALIDATE_CERTS` | Enables SMTP certificate validation. |
| `DOMAIN` | Public host and port used when generating email links. |

## API routes

### General

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/` | Returns the API status message. |

### Authentication

| Method | Endpoint | Authentication | Description |
| --- | --- | --- | --- |
| POST | `/v1/auth/signup` | No | Creates an account and queues a verification email. |
| POST | `/v1/auth/login` | No | Returns access and refresh tokens. |
| POST | `/v1/auth/verify` | Access token | Queues another verification email. |
| GET | `/v1/auth/verify/{safe_token}` | No | Verifies the account associated with the email token. |
| POST | `/v1/auth/refresh-token` | Refresh token | Returns a new access token. |
| GET | `/v1/auth/me` | Access token + role | Returns the current user with books and reviews. |
| POST | `/v1/auth/logout` | Access token | Blocklists the current access token. |
| GET | `/v1/auth/reset_pass` | Access token | Queues a password-reset email. |
| PATCH | `/v1/auth/reset_pass/{token}` | No | Sets a new password using the reset token. |

### Books

All book routes require an access token from an `admin` or `user` account.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/v1/books/` | Lists all books, newest first. |
| GET | `/v1/books/my_books` | Lists books created by the current user. |
| POST | `/v1/books/` | Creates a book for the current user. |
| GET | `/v1/books/{bid}` | Retrieves a book and its reviews. |
| PATCH | `/v1/books/{bid}` | Updates a book by UUID. |
| DELETE | `/v1/books/{bid}` | Deletes a book by UUID. |

### Reviews

All review routes require an access token from an `admin` or `user` account.

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/v1/books/{book_uid}/reviews` | Adds a review to a book. |
| GET | `/v1/reviews/me` | Lists reviews written by the current user. |

## Authentication

Send access tokens to protected routes in the standard bearer header:

```http
Authorization: Bearer <access_token>
```

The refresh endpoint accepts a refresh token in the same format. Logging out stores the access token's `jti` in Redis, preventing that token from being used again.

## Data model

- A user can create many books and write many reviews.
- A book belongs to a user and can have many reviews.
- A review belongs to one user and one book.
- Reviews support ratings from 1 through 5.

## Testing

Run the test suite with:

```bash
uv run pytest
```

## Migrations

Apply all migrations:

```bash
uv run alembic upgrade head
```

Create an autogenerated migration after changing the SQLModel tables:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

# Bookly FastAPI

Bookly is a REST API for a book review service built with FastAPI, SQLModel, PostgreSQL, Redis, JWT authentication, and Alembic migrations.

The project uses a layered structure with routers, schemas, services, database models, authentication dependencies, custom middleware, and centralized custom error handlers.

## Features

* User signup and login
* JWT access and refresh token authentication
* Token logout using Redis blocklist
* Role-based route protection
* Create, read, update, and delete books
* Get books created by the logged-in user
* Add reviews to books
* Get reviews written by the logged-in user
* View a book with its reviews
* Async PostgreSQL database operations
* Alembic database migrations
* Custom HTTP request logging middleware
* Centralized custom exception handling

## Tech Stack

* Python 3.14+
* FastAPI
* SQLModel
* SQLAlchemy Async
* PostgreSQL
* asyncpg
* Alembic
* Redis
* PyJWT
* pwdlib with Argon2
* Pydantic Settings
* Uvicorn
* uv

## Project Structure

```text
Bookly/
├── src/
│   ├── __init__.py              # FastAPI app, router registration, middleware/errors setup
│   ├── config.py                # Environment-based app settings
│   ├── errors.py                # Custom exceptions and handlers
│   ├── middleware.py            # Custom request logging middleware
│   ├── auth/
│   │   ├── dependencies.py      # JWT bearer classes, current-user dependency, role checker
│   │   ├── routes.py            # Signup, login, refresh, me, logout routes
│   │   ├── schemas.py           # Auth/user request and response schemas
│   │   ├── service.py           # User database operations
│   │   └── utils.py             # Password hashing and JWT helpers
│   ├── books/
│   │   ├── book_routes.py       # Book routes
│   │   ├── schemas.py           # Book request and response schemas
│   │   └── service.py           # Book database operations
│   ├── db/
│   │   ├── main.py              # Async database engine and session dependency
│   │   ├── model.py             # SQLModel tables: User, TableBook, Reviews
│   │   └── redis_client.py      # Redis token blocklist helpers
│   └── reviews/
│       ├── routes.py            # Review routes
│       ├── schemas.py           # Review request and response schemas
│       └── service.py           # Review database operations
├── migration_fol/
│   ├── env.py                   # Alembic migration environment
│   ├── script.py.mako
│   └── versions/                # Migration files
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Subhrodeep0019/Bookly-FastAPI.git
cd Bookly-FastAPI
```

Install dependencies:

```bash
uv sync
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/bookly
JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
REDIS_HOST=localhost
REDIS_PORT=6379
```

Make sure PostgreSQL and Redis are running before starting the API.

Run database migrations:

```bash
uv run alembic upgrade head
```

Run the application:

```bash
uv run uvicorn src:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Async PostgreSQL database URL used by SQLAlchemy |
| `JWT_SECRET` | Yes | Secret key used to sign JWT tokens |
| `JWT_ALGORITHM` | Yes | JWT signing algorithm, for example `HS256` |
| `REDIS_HOST` | No | Redis host, defaults to `localhost` |
| `REDIS_PORT` | No | Redis port, defaults to `6379` |

## API Routes

### Root

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| GET | `/` | No | Health check route |

### Auth

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | `/v1/auth/signup` | No | Create a new user |
| POST | `/v1/auth/login` | No | Login and receive access and refresh tokens |
| POST | `/v1/auth/refresh-token` | Refresh token | Create a new access token |
| GET | `/v1/auth/me` | Access token | Get the current user with books and reviews |
| POST | `/v1/auth/logout` | Access token | Blocklist the current access token |

### Books

All book routes require a valid access token and an allowed role of `admin` or `user`.

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/v1/books/` | Get all books ordered by newest first |
| GET | `/v1/books/my_books` | Get books created by the logged-in user |
| POST | `/v1/books/` | Create a new book |
| GET | `/v1/books/{bid}` | Get one book by UUID, including its reviews |
| PATCH | `/v1/books/{bid}` | Update a book by UUID |
| DELETE | `/v1/books/{bid}` | Delete a book by UUID |

### Reviews

All review routes require a valid access token and an allowed role of `admin` or `user`.

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/v1/books/{book_uid}/reviews` | Add a review to a book |
| GET | `/v1/reviews/me` | Get reviews written by the logged-in user |

## Authentication Flow

After login, the API returns:

* `access_token`
* `refresh_token`
* basic user data

Protected routes expect this header:

```http
Authorization: Bearer <access_token>
```

The refresh-token route expects a refresh token in the same bearer format. Access tokens and refresh tokens are validated by separate bearer dependencies, so using the wrong token type returns a custom error response.

Logout blocklists the access token's `jti` value in Redis for 10 minutes.

## Data Models

The main database tables are:

* `users`
* `books`
* `reviews`

Relationships:

* A user can create many books.
* A user can write many reviews.
* A book can have many reviews.
* A review belongs to one user and one book.

## Custom Middleware

The app registers a custom HTTP middleware in `src/middleware.py`.

It logs each request with:

* client host and port
* HTTP method
* request path
* status code and status phrase
* processing time in milliseconds

Example log format:

```text
127.0.0.1:55000 - GET - /v1/books/ - 200 OK - 15.23ms
```

The default `uvicorn.access` logger is disabled so this custom log format is used instead.

## Custom Error Handling

Custom app exceptions are defined in `src/errors.py` and registered on app startup through `register_all_errors(app)`.

Current custom errors include:

* `InvalidToken`
* `RevokedToken`
* `AccessTokenRequired`
* `RefreshTokenRequired`
* `UserAlreadyExists`
* `InvalidCredentials`
* `InsufficientPermission`
* `UserNotFound`
* `BookNotFound`

Each handler returns a consistent JSON response with an HTTP status code and an `error_code`.

Example:

```json
{
  "message": "Book not found",
  "error_code": "book_not_found"
}
```

## Database Migrations

Alembic is configured through `alembic.ini`, and migration files are stored in `migration_fol/versions`.

Apply migrations:

```bash
uv run alembic upgrade head
```

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "migration message"
```

## Current Learning Focus

This project currently practices:

* FastAPI routing and dependency injection
* Async database sessions with SQLModel and SQLAlchemy
* JWT authentication with access and refresh tokens
* Password hashing with Argon2
* Redis-backed token revocation
* Role-based access control
* Centralized error handling
* Middleware-based request logging
* Alembic migration workflow
* Layered backend project organization

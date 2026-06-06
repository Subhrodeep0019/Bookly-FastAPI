# Bookly FastAPI

A RESTful Book Management API built with FastAPI, SQLModel, and PostgreSQL.

This project demonstrates the implementation of a backend service using asynchronous database operations, layered architecture, and CRUD functionality.

## Features

* Create a new book
* Retrieve all books
* Retrieve a single book by UID
* Update book details
* Delete a book
* Async database operations using SQLAlchemy and SQLModel

## Tech Stack

* Python
* FastAPI
* SQLModel
* SQLAlchemy (Async)
* PostgreSQL
* uvicorn
* UV

## Project Structure

```text
src/
├── books/
│   ├── model.py
│   ├── schemas.py
│   ├── service.py
│   └── book_routes.py
├── db/
│   └── main.py
├── config.py
└── __init__.py
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

Create a `.env` file:

```env
DATABASE_URL=your_database_url
```

Run the application:

```bash
uvicorn src:app --reload
```

## API Endpoints

| Method | Endpoint            | Description       |
| ------ |---------------------| ----------------- |
| POST   | /api/v1/books       | Create a book     |
| GET    | /api/v1/books       | Get all books     |
| GET    | /api/v1/books/{uid} | Get a single book |
| PUT    | /api/v1/books/{uid} | Update a book     |
| DELETE | /api/v1/books/{uid} | Delete a book     |

## Learning Outcomes

Through this project, I practiced:

* Building REST APIs with FastAPI
* Async database programming
* Dependency Injection
* Service-based project structure
* PostgreSQL integration
* Git and GitHub workflow


## Challenges & Learnings

As this was my first backend project using FastAPI and PostgreSQL, I faced several challenges while building it:

* Designing the database model and creating separate schemas for creating, updating, and returning book data was initially confusing. Understanding why different models are needed for different operations took some time.

* Working with SQLModel and SQLAlchemy together was challenging because similar functionality often comes from different libraries. Knowing what to import and when to use each library required a lot of reading and experimentation.

* Setting up the database connection was one of the most difficult parts of the project. Learning how asynchronous engines, sessions, and dependency injection work in FastAPI helped me understand how database interactions are managed in real applications.

* Writing database queries using SQLModel's Python syntax was different from writing raw SQL queries. It took practice to understand how ORM queries are constructed and executed.

* Understanding the flow of data through routers, services, schemas, and database models was challenging at first. Building the CRUD operations helped me understand how different layers of a backend application work together.

* Managing asynchronous functions (`async`/`await`) and ensuring database operations were performed correctly required careful debugging and testing.

Through these challenges, I gained practical experience with FastAPI, SQLModel, PostgreSQL, asynchronous programming, API design, and project organization.



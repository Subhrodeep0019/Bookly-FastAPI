from fastapi import FastAPI
from src.books.book_routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db

@asynccontextmanager
async def life_span(app:FastAPI):
    print("Server is starting...")
    await init_db()
    yield
    print("Server is stopped")


ver = "v1"
app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version = ver,
    lifespan=life_span
)
app.include_router(book_router, prefix=f"/api/{ver}/books")

@app.get("/")
async def home():
    return {"msg": "api running live"}
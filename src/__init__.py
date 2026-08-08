from fastapi import FastAPI
from src.books.book_routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from .errors import register_all_errors
from .middleware import register_middleware

ver = "v1"
app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version = ver
)

register_all_errors(app)
register_middleware(app)

app.include_router(book_router, prefix=f"/{ver}/books", tags=["books"])
app.include_router(auth_router,  prefix=f"/{ver}/auth")
app.include_router(review_router,  prefix=f"/{ver}", tags=["reviews"])

@app.get("/")
async def home():
    return {"msg": "api running live"}

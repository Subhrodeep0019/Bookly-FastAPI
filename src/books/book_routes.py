from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from uuid import UUID
from src.books.schemas import ModelBook, ModelCreateBook, ModelUpdBook
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from typing import List

book_router = APIRouter()
book_service = BookService()

@book_router.get(
    "/",
    response_model = List[ModelBook]
) # response_model only verifies at last (while returning) and response matches ModelBook
async def get_all_books(session: AsyncSession = Depends(get_session)):
    all_books = await book_service.get_all_books(session)
    return all_books


# receives JSON, converted into pydantic obj while received in arg, then model_dump() convert it into dict.
@book_router.post(
    "/",
    status_code = status.HTTP_201_CREATED,
    response_model=ModelBook
)
async def add_book(bookData: ModelCreateBook, session: AsyncSession = Depends(get_session)):
    new_created_book = await book_service.create_book(bookData, session)

    return new_created_book


@book_router.get(
    "/{bid}",
    response_model=ModelBook
)
async def get_a_book(bid: UUID, session: AsyncSession = Depends(get_session)):
    single_book = await book_service.get_a_book(bid, session)
    if single_book:
        return single_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "book not found"
        )

@book_router.patch(
    "/{bid}",
    response_model=ModelBook
)
async def upd_book(bid: UUID, updData: ModelUpdBook, session: AsyncSession = Depends(get_session)):
    updated_book = await book_service.update_book(bid, updData, session)
    if updated_book:
        return updated_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found"
        )

@book_router.delete(
    "/{bid}",
    status_code=status.HTTP_200_OK,
    response_model=ModelBook
)
async def del_book(bid: UUID, session: AsyncSession = Depends(get_session)):
    deleted_book = await book_service.delete_book(bid, session)
    if deleted_book:
        return deleted_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book not found"
        )

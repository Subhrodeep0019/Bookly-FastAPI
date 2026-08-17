from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from typing import List

from .schemas import (
    ModelBook,
    ModelCreateBook,
    ModelUpdBook,
    BookWithReview
)

from src.db.main import get_session
from src.books.service import BookService, get_book_service
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.errors import BookNotFound

access_token_bearer = AccessTokenBearer()
admin_user_role_checker = RoleChecker(["admin", "user"])

# Depends(access_token_bearer), #removed
book_router = APIRouter(dependencies=[
    Depends(admin_user_role_checker),
])


@book_router.get(
    "/",
    response_model = List[ModelBook]
) # response_model only verifies at last (while returning) and response matches ModelBook
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    book_service: BookService = Depends(get_book_service)
):
    all_books = await book_service.get_all_books(session)
    return all_books

@book_router.get(
    "/my_books",
    response_model = List[ModelBook]
)
async def get_my_books(
        session: AsyncSession = Depends(get_session),
        book_service: BookService = Depends(get_book_service),
        payload: dict = Depends(access_token_bearer),
):
    my_uid = UUID(payload.get('user').get('user_uid'))
    my_books = await book_service.get_my_books(my_uid, session)
    return my_books


# receives JSON, converted into pydantic obj while received in arg, then model_dump() convert it into dict.
@book_router.post(
    "/",
    status_code = status.HTTP_201_CREATED,
    response_model=ModelBook
)
async def add_book(
    bookData: ModelCreateBook,
    session: AsyncSession = Depends(get_session),
    book_service: BookService = Depends(get_book_service),
    payload: dict = Depends(access_token_bearer),
):
    user_uid = payload.get('user').get('user_uid')
    new_created_book = await book_service.create_book(bookData, user_uid, session)

    return new_created_book


@book_router.get(
    "/{bid}",
    response_model=BookWithReview
)
async def get_a_book(
    bid: UUID,
    session: AsyncSession = Depends(get_session),
    book_service: BookService = Depends(get_book_service),
):
    single_book = await book_service.get_a_book(bid, session)
    if not single_book:
        raise BookNotFound()

    return single_book


@book_router.patch(
    "/{bid}",
    response_model=ModelBook
)
async def upd_book(
    bid: UUID, updData: ModelUpdBook,
    session: AsyncSession = Depends(get_session),
    book_service: BookService = Depends(get_book_service),
):
    updated_book = await book_service.update_book(bid, updData, session)
    if not updated_book:
        raise BookNotFound()

    return updated_book


@book_router.delete(
    "/{bid}",
    status_code=status.HTTP_200_OK,
    response_model=ModelBook
)
async def del_book(
    bid: UUID,
    session: AsyncSession = Depends(get_session),
    book_service: BookService = Depends(get_book_service),
):
    deleted_book = await book_service.delete_book(bid, session)
    if not deleted_book:
        raise BookNotFound()

    return deleted_book

from typing import List
from fastapi import APIRouter, status, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.db.model import User
from .service import ReviewService
from .schemas import ReviewCreateModel, ReviewResponseModel
from src.auth.dependencies import AccessTokenBearer, RoleChecker, get_curr_user
from uuid import UUID


review_service = ReviewService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


review_router = APIRouter(dependencies=[
    Depends(access_token_bearer),
    Depends(role_checker)
])


@review_router.post(
    "/books/{book_uid}/reviews",
    response_model= ReviewResponseModel,
    status_code=status.HTTP_201_CREATED
)
async def add_review(
    book_uid: UUID,
    review: ReviewCreateModel,
    curr_user: User = Depends(get_curr_user),
    session: AsyncSession = Depends(get_session)
):
    created_review = await review_service.add_review(book_uid, curr_user, review, session)
    return created_review


@review_router.get(
    "/reviews/me",
    response_model= List[ReviewResponseModel]
)
async def get_my_reviews(
        curr_user: User = Depends(get_curr_user),
        session: AsyncSession = Depends(get_session)
):
    rev_list = await review_service.get_my_reviews(curr_user, session)
    return rev_list




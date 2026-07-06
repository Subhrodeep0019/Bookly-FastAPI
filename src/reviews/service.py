from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from fastapi import status
from fastapi.exceptions import HTTPException
from .schemas import ReviewCreateModel
from src.db.model import Reviews, User
from src.books.service import BookService
from src.errors import BookNotFound

book_service = BookService()

class ReviewService:

    async def add_review(
            self,
            book_id: UUID,
            user: User,
            review: ReviewCreateModel,
            session: AsyncSession
    ) -> Reviews | None:
        user_id = user.uid
        book = await book_service.get_a_book(book_id, session)
        if not book:
            raise BookNotFound()
        curr_review = Reviews(**(review.model_dump()))
        curr_review.book_uid, curr_review.user_uid = book_id, user_id

        # curr_review.book, curr_review.user = book, user

        try:
            session.add(curr_review)
            await session.commit()
            await session.refresh(curr_review)
            return curr_review
        except SQLAlchemyError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OOPS... Something Went Wrong"
            )

    async def get_my_reviews(
            self,
            user: User,
            session: AsyncSession
    ): # -> List[Reviews]
        user_id = user.uid
        statement = select(Reviews).where(user_id == Reviews.user_uid).order_by(desc(Reviews.created_at))
        try:
            review_list = await session.exec(statement)
            return review_list.all()
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OOPS... Something Went Wrong"
            )
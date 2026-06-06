import datetime

from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID
from .model import TableBook as Book
from sqlmodel import select, desc
from .schemas import ModelCreateBook, ModelUpdBook

class BookService:
    async def get_all_books(self, session: AsyncSession):

        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)

        return result.all() # returns a list of book obj


    async def get_a_book(self, book_uid: UUID, session: AsyncSession):

        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)

        # returns None if no books is found
        return result.first() # returns a Book obj

    async def create_book(self, book_details: ModelCreateBook, session: AsyncSession):

        book_details_dict = book_details.model_dump()
        new_book = Book(**book_details_dict)   #unpacks dict and Book() creates a TableBook obj and saves into new_book

        session.add(new_book) # obj enter into session's pending state
        await session.commit() # actual SQL command is sent to psql
        await session.refresh(new_book)

        return new_book


    async def update_book(self,book_uid: UUID, upd_details: ModelUpdBook, session: AsyncSession):

        book_to_upd = await self.get_a_book(book_uid, session)

        if book_to_upd is not None:
            upd_details_dict = upd_details.model_dump(exclude_unset=True)
            for k, v in upd_details_dict.items():
                setattr(book_to_upd, k, v)
            book_to_upd.updated_at = datetime.datetime.now()
            await session.commit()
            await session.refresh(book_to_upd)
            return book_to_upd
        else:
            return None


    async def delete_book(self, book_uid: UUID, session: AsyncSession):
        book_to_delete = await self.get_a_book(book_uid, session)

        if book_to_delete is not None:
                await session.delete(book_to_delete)
                await session.commit()

        return book_to_delete

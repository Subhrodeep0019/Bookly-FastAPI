from .schemas import UserCreateModel
from .model import User
from .utils import generate_hash
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

class UserService:

    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email==email)
        res = await session.exec(statement)
        # returns 'None' if user doesn't exist
        return res.first()

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession) -> User|None:
        # convert into 'User' ORM
        my_user = User(**(user_data.model_dump()))

        existing_user = await self.get_user(my_user.email, session)
        if existing_user is None:

            hashed_pass = generate_hash(my_user.pswd)
            my_user.pswd = hashed_pass

            session.add(my_user)
            await session.commit()
            await session.refresh(my_user)
            return my_user
        else:
            # return None if user already exists
            return None
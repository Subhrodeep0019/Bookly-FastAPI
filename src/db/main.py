from sqlmodel import SQLModel

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.ext.asyncio import create_async_engine
from src.config import setting

engine = create_async_engine(
    url=setting.DATABASE_URL,
    echo=True
)

async def init_db():
    async with engine.begin() as conn:
        from src.books.model import TableBook

        await conn.run_sync(SQLModel.metadata.create_all)

# session factory config
Session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

async def get_session():
    async with Session() as session:
        yield session
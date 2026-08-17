from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import setting

engine = create_async_engine(
    url=setting.DATABASE_URL
)

# session factory config
Session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

async def get_session():
    async with Session() as session:
        yield session
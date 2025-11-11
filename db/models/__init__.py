from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

mysql_url = "mysql+aiomysql://root:1234567890@localhost/todo"

asyne_engine = create_async_engine(mysql_url, echo=True)
AsyncSessionLocal = async_sessionmaker(asyne_engine, expire_on_commit=False, autoflush=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
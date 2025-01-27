from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from tgbot.config import Config
from tgbot.services.utils import make_connection_string


async def create_db_session(config: Config):
    engine = create_async_engine(
        make_connection_string(config),
        future=True,
        pool_size=50,
        max_overflow=0
    )

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    return async_session

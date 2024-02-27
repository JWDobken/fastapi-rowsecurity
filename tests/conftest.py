from typing import AsyncGenerator

import pytest_asyncio
from faker import Faker
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .simple_model import Base, Item, User

WRITEUSER = "writeuser"
WRITEUSERPASSWORD = "writepassword"


@pytest_asyncio.fixture()
async def simple_session_user1() -> AsyncGenerator[AsyncSession, None]:
    """Return a session with user 1 for the simple model."""

    superuser_engine = create_async_engine(
        "postgresql+asyncpg://jwdobken:postgres@127.0.0.1:5432/test_db",
        echo=True,
        future=True,
    )

    async with superuser_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    superuser_session = async_sessionmaker(superuser_engine)()

    await superuser_session.execute(
        text(
            f"""DO $$
            BEGIN
                BEGIN
                    CREATE ROLE {WRITEUSER} WITH LOGIN PASSWORD '{WRITEUSERPASSWORD}';
                EXCEPTION WHEN duplicate_object THEN
                    NULL;
                END;
            END $$;
            ;"""
        )
    )
    await superuser_session.execute(
        text(f"GRANT CONNECT ON DATABASE test_db TO {WRITEUSER};")
    )
    await superuser_session.execute(
        text(
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {WRITEUSER};"
        )
    )
    await superuser_session.commit()

    # Insert some fake data using Faker
    faker = Faker()
    users = [User(username=faker.user_name()) for _ in range(5)]
    superuser_session.add_all(users)
    await superuser_session.commit()

    # Create a couple of items owned by the users
    for user in users:
        item1 = Item(title=faker.word(), owner=user)
        item2 = Item(title=faker.word(), owner=user)
        superuser_session.add(item1)
        superuser_session.add(item2)
    await superuser_session.commit()
    await superuser_session.close()

    # RETURN WRITE USERSESSION
    writeuser_engine = create_async_engine(
        f"postgresql+asyncpg://{WRITEUSER}:{WRITEUSERPASSWORD}@127.0.0.1:5432/test_db",
        echo=True,
        future=True,
    )
    writeuser_session = async_sessionmaker(writeuser_engine)()
    await writeuser_session.execute(text(f"SET app.current_user_id = 1"))
    yield writeuser_session
    await writeuser_session.close()

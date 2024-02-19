from typing import AsyncGenerator

import pytest_asyncio
from faker import Faker
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "postgresql+asyncpg://jwdobken:postgres@127.0.0.1:5432/test_db", echo=True, future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    session = async_sessionmaker(engine)()

    # Insert some fake data using Faker
    faker = Faker()
    users = [User(username=faker.user_name()) for _ in range(5)]
    session.add_all(users)
    await session.commit()

    # Create a couple of items owned by the users
    for user in users:
        item1 = Item(title=faker.word(), owner=user)
        item2 = Item(title=faker.word(), owner=user)
        session.add(item1)
        session.add(item2)
    await session.commit()

    yield session
    await session.close()

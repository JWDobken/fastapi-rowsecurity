from typing import Dict, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from examples.simple import Base, User, app, get_session

TEST_DB_URL_ADMIN = "postgresql://postgres:postgres@0.0.0.0:5432/test"
TEST_DB_URL_WRITE = "postgresql://app_db_write:V11Xn3#c3$4r@0.0.0.0:5432/test"


@pytest.fixture(scope="session")
def session(test_db_setup_sessionmaker) -> Generator[Session, None, None]:
    with get_session() as session:
        yield session


def fill_user_database(engine):
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as session:
        db_user1 = User(username="user1", password="password1")
        db_user2 = User(username="user2", password="password2")
        session.add(db_user1)
        session.add(db_user2)
        session.commit()

        session.execute(
            text(
                """
    GRANT CONNECT ON DATABASE test TO app_db_write;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_db_write;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_db_write;
"""
            )
        )
        session.commit()


def create_db():
    engine = create_engine(TEST_DB_URL_ADMIN)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    fill_user_database(engine)


def drop_db():
    engine = create_engine(TEST_DB_URL_ADMIN)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client() -> Generator:
    create_db()
    with TestClient(app) as c:
        yield c

    # item = Item(
    #     title=fake.sentence(nb_words=random.randint(2, 4)), description=fake.paragraph(), user_id=current_user.id
    # )

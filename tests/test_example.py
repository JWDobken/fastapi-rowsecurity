import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_number_of_users(db_session):
    # Get the number of users from the database
    result = await db_session.execute(text("SELECT COUNT(*) FROM users"))
    num_users = result.scalar_one()

    assert num_users == 5


@pytest.mark.asyncio
async def test_number_of_items(db_session):
    # Get the number of items from the database
    result = await db_session.execute(text("SELECT COUNT(*) FROM items"))
    num_items = result.scalar_one()

    assert num_items == 10

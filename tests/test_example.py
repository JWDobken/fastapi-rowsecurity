import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_number_of_users(session_example_1):
    session = session_example_1
    # Get the number of users from the database
    result = await session.execute(text("SELECT COUNT(*) FROM users"))
    num_users = result.scalar_one()

    assert num_users == 5


@pytest.mark.asyncio
async def test_number_of_items(session_example_1):
    session = session_example_1
    # Get the number of items from the database
    result = await session.execute(text("SELECT COUNT(*) FROM items"))
    num_items = result.scalar_one()

    assert num_items == 10


@pytest.mark.asyncio
async def test_number_of_users(session_example_1):
    session = session_example_1
    # Get the number of users from the database
    result = await session.execute(text("SELECT COUNT(*) FROM users"))
    num_users = result.scalar_one()

    assert num_users == 5


@pytest.mark.asyncio
async def test_owner_can_edit(session_example_1):
    session = session_example_1
    # edit an item that is owned by user 1
    result = await session.execute(text("SELECT id FROM items where owner_id =1 limit 1"))
    item_id = result.scalar_one()
    statement = f"""
    UPDATE items
    SET title = 'user_1_can_edit_its_own_items'
    WHERE id = {item_id}
    """
    await session.execute(text(statement))
    await session.commit()


@pytest.mark.asyncio
async def test_nonowner_cannot_edit(session_example_1):
    session = session_example_1
    # edit an item that is NOT owned by user 1
    result = await session.execute(text("SELECT id FROM items where owner_id != 1 limit 1"))
    item_id = result.scalar_one()
    statement = f"""
    UPDATE items
    SET title = 'user_1_can_edit_other_items'
    WHERE id = {item_id}
    """
    await session.execute(text(statement))
    await session.commit()

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm.exc import StaleDataError

from .simple_model import Item, User


@pytest.mark.asyncio
async def test_number_of_users(simple_session_user1):
    session = simple_session_user1
    # Get the number of users from the database
    stmt = select(func.count(User.id))
    result = await session.execute(stmt)
    num_users = result.scalar()
    assert num_users == 5


@pytest.mark.asyncio
async def test_number_of_items(simple_session_user1):
    session = simple_session_user1
    # Get the number of items from the database
    stmt = select(func.count(Item.id))
    result = await session.execute(stmt)
    num_items = result.scalar()
    # user 1 can read all items
    assert num_items == 10


@pytest.mark.asyncio
async def test_create_own_item(simple_session_user1):
    session = simple_session_user1
    # create an item that is owned by user 1
    new_item = Item(id=11, title="its mine!", owner_id=1)
    session.add(new_item)
    await session.commit()


@pytest.mark.asyncio
async def test_create_other_item(simple_session_user1):
    session = simple_session_user1
    # create an item that is not owned by user 1
    with pytest.raises(
        ProgrammingError,
        match=r'.*new row violates row-level security policy for table "items"',
    ):
        new_item = Item(id=11, title="its mine!", owner_id=2)
        session.add(new_item)
        await session.commit()


@pytest.mark.asyncio
async def test_edit_own_item(simple_session_user1):
    session = simple_session_user1
    # edit an item that is owned by user 1
    stmt = select(Item).filter(Item.owner_id == 1).limit(1)
    result = await session.execute(stmt)
    item: Item = result.scalar_one()
    item.title = "user_1_can_edit_its_own_items"
    await session.commit()


@pytest.mark.asyncio
async def test_edit_other_item(simple_session_user1):
    session = simple_session_user1
    # edit an item that is not owned by user 1
    stmt = select(Item).filter(Item.owner_id != 1).limit(1)
    with pytest.raises(StaleDataError):
        result = await session.execute(stmt)
        item: Item = result.scalar_one()
        item.title = "user_1_cannot_edit_other_items"
        await session.commit()


@pytest.mark.asyncio
async def test_delete_own_item(simple_session_user1):
    session = simple_session_user1
    # delete an item that is owned by user 1
    stmt = select(Item).filter(Item.owner_id == 1).limit(1)
    result = await session.execute(stmt)
    item: Item = result.scalar_one()
    await session.delete(item)
    await session.commit()
    # SOMEHOW THIS NEVER GIVES AN ERROR!!
    stmt = select(func.count(Item.id))
    result = await session.execute(stmt)
    num_items = result.scalar()
    # user 1 can read all items
    assert num_items == 9


@pytest.mark.asyncio
async def test_delete_other_item(simple_session_user1):
    session = simple_session_user1
    # delete an item that is not owned by user 1
    stmt = select(Item).filter(Item.owner_id != 1).limit(1)
    result = await session.execute(stmt)
    item: Item = result.scalar_one()
    await session.delete(item)
    await session.commit()
    # SOMEHOW THIS NEVER GIVES AN ERROR!!
    stmt = select(func.count(Item.id))
    result = await session.execute(stmt)
    num_items = result.scalar()
    # user 1 can read all items
    assert num_items == 10

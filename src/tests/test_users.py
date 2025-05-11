import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.users import UserCreate
from postgres.models.users import User
from msgspec import structs


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user_data = UserCreate(
        first_name='John',
        last_name='Bond',
        email='johnbond@email.com',
    )
    user = User(**structs.asdict(user_data))
    db_session.add(user)
    await db_session.commit()
    result = await db_session.execute(
        select(User).where(User.email == 'johnbond@email.com')
    )
    fetched_user = result.scalar_one()
    assert fetched_user.first_name == 'John'
    assert fetched_user.email == 'johnbond@email.com'

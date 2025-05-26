import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.users import UserCreate, UserLogin
from postgres.models.users import User
from msgspec import structs
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    user_data = UserCreate(
        first_name='John',
        last_name='Bond',
        username='jobond',
        password='12345',
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


@pytest.mark.asyncio
async def test_login_invalid_credentials(db_session: AsyncSession, test_client):
    # 1. Создаем пользователя с некорректным паролем
    user_data = UserCreate(
        first_name='John',
        last_name='Bond',
        username='jobond',
        password='12345',
        email='johnbond@email.com',
    )
    user_dict = structs.asdict(user_data)
    password = user_dict.pop('password')
    user = User(**user_data, hashed_password=pwd_context.hash('wrong-pass'))
    db_session.add(user)
    await db_session.commit()

    # Данные для логина
    login_data = UserLogin(username=user.username, password=password)

    # Отправка POST-запроса через тестовый клиент
    response = await test_client.post('/users/login', json=structs.asdict(login_data))

    # Проверка результата
    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid credentials'

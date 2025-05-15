from litestar import Controller, get, post, patch, delete
from litestar.di import Provide
from litestar.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.users import UserCreate, UserPatch, UserLogin, UserRead
from src.postgres.models.users import User
from src import app
from msgspec import structs, to_builtins
from litestar.pagination import OffsetPagination
from litestar.plugins.sqlalchemy import filters, repository
from uuid import UUID
from passlib.context import CryptContext
from litestar.dto import MsgspecDTO

__all__ = (
    'UserController',
    'UsersRepository',
    'provide_users_repo',
)

pwd_context = CryptContext(schemes=['sha256_crypt'])


class UsersRepository(repository.SQLAlchemyAsyncRepository[User]):
    """Author repository."""

    model_type = User


async def provide_users_repo(db_session: AsyncSession) -> UsersRepository:
    """This provides the default Users repository."""
    return UsersRepository(session=db_session)


class UserController(Controller):
    path = '/users'
    dependencies = {'users_repo': Provide(provide_users_repo)}

    @get(path='/', return_dto=MsgspecDTO[UserRead])
    async def list_users(
        self,
        users_repo: UsersRepository,
        limit_offset: filters.LimitOffset,
    ) -> OffsetPagination[User]:
        """List users."""
        results, total = await users_repo.list_and_count(limit_offset)
        return OffsetPagination[User](
            items=results,
            total=total,
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )

    @post('/login', signature_types=[User])
    async def login(
        self,
        data: UserLogin,
        users_repo: UsersRepository,
    ) -> dict:
        user = await users_repo.get_one_or_none(username=data.username)
        if not user or not pwd_context.verify(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail='Неверный username или пароль')
        token = app.jwt_auth.create_token(identifier=str(user.id))
        return {'access_token': token, 'token_type': 'bearer'}

    @post('/', return_dto=MsgspecDTO[UserRead])
    async def create_user(self, data: UserCreate, users_repo: UsersRepository) -> User:
        """Create new user."""
        user_data = structs.asdict(data)
        password = user_data.pop('password', None)
        user = await users_repo.add(
            User(**user_data, hashed_password=pwd_context.hash(password)),
        )
        await users_repo.session.commit()
        return user

    @get('/{user_id:uuid}', return_dto=MsgspecDTO[UserRead])
    async def get_user(self, user_id: UUID, users_repo: UsersRepository) -> User:
        """Get user."""
        user = await users_repo.get(user_id)
        return user

    @patch('/{user_id:uuid}',  return_dto=MsgspecDTO[UserRead])
    async def update_user(
        self, user_id: UUID, data: UserPatch, users_repo: UsersRepository
    ) -> User:
        """Update user."""
        raw_obj = to_builtins(data)
        raw_obj['id'] = user_id
        user = User(**raw_obj)
        updated_user = await users_repo.update(user)
        await users_repo.session.commit()
        return updated_user

    @delete('/{user_id:uuid}')
    async def delete_user(self, user_id: UUID, users_repo: UsersRepository) -> None:
        await users_repo.delete(user_id)
        await users_repo.session.commit()

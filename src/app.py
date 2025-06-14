from advanced_alchemy.exceptions import IntegrityError
from litestar import Litestar
from litestar.di import Provide
from litestar.contrib.sqlalchemy.plugins import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)
from litestar.connection import ASGIConnection
from litestar.exceptions import ClientException
from litestar.status_codes import HTTP_409_CONFLICT
from litestar.params import Parameter
from litestar.plugins.sqlalchemy import filters, base, SQLAlchemySerializationPlugin
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import SwaggerRenderPlugin
from litestar.logging import LoggingConfig
from litestar.security.jwt import JWTAuth, Token
from uuid import UUID
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.controllers.users import UserController, provide_users_repo
from src.configs.app_config import configure
from src.postgres.models.users import User

__all__ = (
    'on_startup',
    'provide_limit_offset_pagination',
)


config = configure()

logging_config = LoggingConfig(
    root={'level': 'INFO', 'handlers': ['queue_listener']},
    formatters={
        'standart': {'format': '%(asxtime)s - %(name)s - %(levelname)s - %(message)s'}
    },
    log_exceptions='always',
)


async def provide_limit_offset_pagination(
    current_page: int = Parameter(
        query='currentPage',
        ge=1,
        default=1,
        required=False,
    ),
    page_size: int = Parameter(
        query='pageSize',
        ge=1,
        default=10,
        required=False,
    ),
) -> filters.LimitOffset:
    """Add offset/limit pagination.
    Return type consumed by `Repository.apply_limit_offset_pagination()`.
    Parameters
    ----------
    current_page : int
        LIMIT to apply to select.
    page_size : int
        OFFSET to apply to select.
    """
    return filters.LimitOffset(page_size, page_size * (current_page - 1))


sessionmaker = async_sessionmaker(expire_on_commit=False)


async def retrieve_user_handler(
    token: Token,
    connection: ASGIConnection,
) -> User | None:
    user_id = UUID(token.sub)
    users_repo = connection.scope.get('users_repo')
    if not users_repo:
        async with sessionmaker(bind=db_config.get_engine()) as session:
            try:
                async with session.begin():
                    users_repo = await provide_users_repo(db_session=session)
            except IntegrityError as exc:
                raise ClientException(
                    status_code=HTTP_409_CONFLICT,
                    detail=str(exc),
                ) from exc
    user = await users_repo.get(user_id)
    return user


jwt_auth = JWTAuth[User](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=config.jwt.token_secret,
    algorithm='HS256',
    exclude=[
        '/users/login',
        '/schema',
    ],
)

session_config = AsyncSessionConfig(expire_on_commit=False)
db_config = SQLAlchemyAsyncConfig(
    connection_string=config.database.get_connection_url(),
    before_send_handler='autocommit',
    session_config=session_config,
)


async def on_startup() -> None:
    """Initializes the database."""
    async with db_config.get_engine().begin() as conn:
        await conn.run_sync(base.UUIDBase.metadata.create_all)


sqlalchemy_plugin = SQLAlchemyInitPlugin(config=db_config)

app = Litestar(
    route_handlers=[UserController],
    logging_config=logging_config,
    on_startup=[on_startup],
    openapi_config=OpenAPIConfig(
        title='NotaMem',
        version='0.1.0',
        render_plugins=[SwaggerRenderPlugin()],
    ),
    dependencies={'limit_offset': Provide(provide_limit_offset_pagination)},
    plugins=[sqlalchemy_plugin, SQLAlchemySerializationPlugin()],
)

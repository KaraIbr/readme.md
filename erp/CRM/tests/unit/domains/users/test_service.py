import pytest
from core.config import Settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from core.exceptions import AuthorizationError, NotFoundError
from domains.users.service import (
    get_active_user,
    require_crm_service_access,
    user_has_crm_service_access,
)
from helpers import create_iam_user, grant_iam_crm_service_access
from pydantic import SecretStr


@pytest.fixture()
async def session():
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key=SecretStr("super-secret-for-tests"),
    )
    engine = build_async_engine(settings)
    await create_all(engine)
    session_factory = build_session_factory(engine)

    try:
        async with session_factory() as test_session:
            yield test_session
    finally:
        await drop_all(engine)
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_active_user_reads_iam_user_reference(session) -> None:
    user = await create_iam_user(session, email="owner@example.com")

    assert user.id is not None
    resolved = await get_active_user(session, user.id)

    assert resolved.email == "owner@example.com"


@pytest.mark.asyncio
async def test_get_active_user_rejects_missing_or_inactive_user(session) -> None:
    inactive = await create_iam_user(
        session,
        email="inactive@example.com",
        is_active=False,
        crm_service_access=False,
    )
    assert inactive.id is not None

    with pytest.raises(NotFoundError):
        await get_active_user(session, 9999)

    with pytest.raises(AuthorizationError):
        await get_active_user(session, inactive.id)


@pytest.mark.asyncio
async def test_crm_service_access_is_required(session) -> None:
    user = await create_iam_user(
        session,
        email="owner@example.com",
        crm_service_access=False,
    )
    assert user.id is not None

    assert await user_has_crm_service_access(session, user.id) is False
    with pytest.raises(AuthorizationError):
        await require_crm_service_access(session, user.id)

    await grant_iam_crm_service_access(session, user_id=user.id)

    assert await user_has_crm_service_access(session, user.id) is True
    await require_crm_service_access(session, user.id)

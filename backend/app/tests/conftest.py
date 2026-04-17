"""
pytest fixtures shared across all tests.
Uses an in-memory SQLite DB (via aiosqlite) for isolation.
"""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.main import app
from app.dependencies import get_db
from app.utils.auth import hash_password

# ── In-memory test DB ─────────────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once for the test session."""
    # Import all models so Base.metadata knows about them
    from app import models  # noqa
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db() -> AsyncSession:
    """Provides a clean DB session for each test, rolled back after."""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncClient:
    """Async test client with DB override."""
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Helper: create a user directly in DB ─────────────────────────────────────
async def _create_user(db: AsyncSession, email: str, password: str, display_name: str, role: str = "user"):
    from app.crud.user import crud_user
    from app.schemas.user import UserCreate

    obj_in = UserCreate(email=email, password=password, display_name=display_name)
    return await crud_user.create(db, obj_in, hash_password(password))


@pytest_asyncio.fixture
async def user_alice(db: AsyncSession):
    return await _create_user(db, "alice@test.com", "password123", "Alice")


@pytest_asyncio.fixture
async def user_bob(db: AsyncSession):
    return await _create_user(db, "bob@test.com", "password123", "Bob")


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    user = await _create_user(db, "admin@test.com", "adminpass123", "Admin", role="admin")
    user.role = "admin"
    await db.flush()
    return user


@pytest_asyncio.fixture
async def alice_token(client: AsyncClient, user_alice):
    resp = await client.post("/api/v1/auth/login", params={
        "email": "alice@test.com", "password": "password123"
    })
    return resp.json()["data"]["access_token"]


@pytest_asyncio.fixture
async def bob_token(client: AsyncClient, user_bob):
    resp = await client.post("/api/v1/auth/login", params={
        "email": "bob@test.com", "password": "password123"
    })
    return resp.json()["data"]["access_token"]


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient, admin_user):
    resp = await client.post("/api/v1/auth/login", params={
        "email": "admin@test.com", "password": "adminpass123"
    })
    return resp.json()["data"]["access_token"]


@pytest_asyncio.fixture
async def couple_fixture(db: AsyncSession, user_alice, user_bob):
    from datetime import date
    from app.crud.couple import crud_couple

    couple = await crud_couple.create(
        db,
        user1_id=user_alice.id,
        anniversary_date=date(2022, 6, 15),
        couple_name="Alice & Bob",
    )
    couple = await crud_couple.join_couple(db, couple, user_bob.id)
    return couple
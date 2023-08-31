from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DB_URL = "sqlite+aiosqlite:///:memory:"
# TODO: DB_URL = "somepostgresurl..."

engine = create_async_engine(DB_URL)
DbSession = async_sessionmaker(engine, expire_on_commit=False)

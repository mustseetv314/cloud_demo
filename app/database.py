from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database() -> None:
    # CREATE DATABASE must run outside a transaction. Restrict the identifier before
    # interpolating it because SQL Server does not allow a bound database name here.
    if not settings.db_name.replace("_", "").isalnum():
        raise ValueError("DB_NAME may contain only letters, numbers, and underscores")

    master_engine = create_engine(
        settings.database_url("master"), isolation_level="AUTOCOMMIT"
    )
    try:
        with master_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM sys.databases WHERE name = :name"),
                {"name": settings.db_name},
            ).scalar()
            if not exists:
                connection.execute(text(f"CREATE DATABASE [{settings.db_name}]"))
    finally:
        master_engine.dispose()

    # Import here so the model is registered before table creation.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)

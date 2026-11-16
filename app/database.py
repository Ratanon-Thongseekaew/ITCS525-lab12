"""Database connection supplied for Lab 12; history still lives in memory."""
import os
from functools import lru_cache
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy import URL

from app.models import CalculationSession, CalculatorLog


@lru_cache
def get_engine():
    # URL.create also handles passwords containing URL-special characters.
    url = URL.create(
        "postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.getenv("DB_HOST", "database"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.environ["POSTGRES_DB"],
    )
    return create_engine(url, pool_pre_ping=True)


def get_session():
    with Session(get_engine()) as session:
        yield session


def init_db():
    """Initialize database tables."""
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

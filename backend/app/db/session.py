from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.config import get_settings


def create_database_engine() -> Engine:
    """Create the SQLAlchemy engine from application settings."""
    return create_engine(get_settings().database_url, pool_pre_ping=True)


engine = create_database_engine()


def check_database_connection() -> bool:
    """Return True when PostgreSQL accepts a simple query."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

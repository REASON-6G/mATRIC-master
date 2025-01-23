import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
from app.database_session import engine, SessionLocal, Base

def test_database_url():
    expected_url = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    assert engine.url == expected_url

def test_create_engine():
    assert engine is not None
    assert str(engine.url) == f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

def test_session_local():
    session = SessionLocal()
    assert session is not None
    assert session.bind == engine
    session.close()

def test_declarative_base():
    assert Base is not None
    assert hasattr(Base, 'metadata')

def test_session_commit_rollback():
    session = SessionLocal()
    try:
        session.execute('SELECT 1')
        session.commit()
    except Exception:
        session.rollback()
        pytest.fail("Rollback was called due to an exception.")
    finally:
        session.close()

if __name__ == "__main__":
    pytest.main()

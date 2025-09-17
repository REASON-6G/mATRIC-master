# tests/test_database_session.py

import pytest
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker

def test_session_local():
    from app.database_session import SessionLocal, engine
    assert isinstance(SessionLocal, sessionmaker)
    assert SessionLocal.kw['bind'] == engine

def test_base_declaration():
    from app.database_session import Base
    assert hasattr(Base, 'metadata')
    assert hasattr(Base, 'registry')
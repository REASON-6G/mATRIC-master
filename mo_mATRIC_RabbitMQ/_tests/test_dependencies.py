import pytest
from unittest.mock import patch
from app.database import SessionLocal
from app.database_session import get_db

def test_get_db():
    with patch('app.database.SessionLocal') as mock_session:
        mock_session.return_value = MagicMock()
        generator = get_db()
        db = next(generator)
        assert db is mock_session.return_value
        try:
            next(generator)
        except StopIteration:
            pass
        mock_session.return_value.close.assert_called_once()

if __name__ == "__main__":
    pytest.main()

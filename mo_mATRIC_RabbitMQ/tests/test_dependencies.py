# tests/test_dependencies.py

import pytest
from unittest.mock import patch, MagicMock


def test_get_db():
    # Patch SessionLocal in the context of app.database
    with patch('app.database_session.SessionLocal', autospec=True) as mock_session_local:
        # Create a mock session
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session

        # Import get_db after patching
        from app.dependencies import get_db

        # Use the dependency and extract the generator
        db_generator = get_db()

        try:
            # Retrieve the first value from the generator
            db_session = next(db_generator)

            # Verify that a session was created
            mock_session_local.assert_called_once()

            # Verify that the session returned by the dependency is correct
            assert db_session == mock_session
        finally:
            # Ensure the generator's `finally` block is executed
            db_generator.close()

        # Verify that the session's close method was called
        mock_session.close.assert_called_once()
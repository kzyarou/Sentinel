import pytest
from unittest.mock import AsyncMock, patch
from app.db.session import check_db_connection


@pytest.mark.asyncio
async def test_check_db_connection_success():
    """Test successful database connection check."""
    with patch('app.db.session.engine') as mock_engine:
        mock_conn = AsyncMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn
        mock_conn.execute.return_value = AsyncMock()
        
        result = await check_db_connection()
        assert result is True


@pytest.mark.asyncio
async def test_check_db_connection_failure():
    """Test failed database connection check."""
    with patch('app.db.session.engine') as mock_engine:
        mock_engine.connect.side_effect = Exception("Connection failed")
        
        result = await check_db_connection()
        assert result is False

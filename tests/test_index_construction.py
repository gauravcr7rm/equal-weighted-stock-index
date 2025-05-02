import sys
import os
from pathlib import Path
import pytest
from datetime import date, timedelta

# Add the parent directory to sys.path to allow importing app modules
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from app.services.index_construction import construct_equal_weighted_index
from app.db.database import reset_db, init_db

@pytest.fixture(scope="module")
def setup_test_db():
    """Set up a test database."""
    # Use an in-memory database for testing
    os.environ["DB_PATH"] = ":memory:"
    
    # Initialize the database
    init_db()
    
    yield
    
    # Clean up
    reset_db()

def test_construct_index_empty_db(setup_test_db):
    """Test index construction with an empty database."""
    # Define test dates
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Attempt to construct index
    result = construct_equal_weighted_index(yesterday, today)
    
    # Verify result
    assert result['success'] is False
    assert "No trading data available" in result['message']

# Add more tests as needed

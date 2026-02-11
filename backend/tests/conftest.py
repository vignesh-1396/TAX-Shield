"""
Test configuration and fixtures for ITC Shield
"""
import pytest
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment BEFORE importing app
os.environ["DATABASE_URL"] = ""  # Use SQLite for tests
os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Separate test DB
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing_only_minimum_32_characters_long"
os.environ["GSP_MODE"] = "mock"  # Use mock GSP for tests

from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def client():
    """FastAPI test client - import app only when needed"""
    from app.main import app
    return TestClient(app)

@pytest.fixture
def test_db():
    """Test database connection"""
    from app.db.session import get_connection, init_database
    
    # Initialize test database
    init_database()
    
    yield
    
    # Cleanup after tests
    try:
        with get_connection() as (conn, cursor):
            cursor.execute("DELETE FROM compliance_checks")
            cursor.execute("DELETE FROM batch_jobs")
            cursor.execute("DELETE FROM batch_items")
            cursor.execute("DELETE FROM vendors")
            cursor.execute("DELETE FROM users")
            conn.commit()
    except Exception:
        pass  # Ignore cleanup errors

@pytest.fixture
def sample_gstin():
    """Valid GSTIN for testing"""
    return "27AABCU9603R1ZM"

@pytest.fixture
def sample_vendor_data():
    """Sample vendor data for testing"""
    return {
        "gstin": "27AABCU9603R1ZM",
        "legal_name": "TEST COMPANY PVT LTD",
        "trade_name": "TEST CO",
        "gst_status": "Active",
        "registration_date": "2020-01-15"
    }

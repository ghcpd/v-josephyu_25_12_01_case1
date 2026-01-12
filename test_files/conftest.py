"""
Pytest configuration and fixtures for Flask Log Management System tests
"""
import os
import sys
import pytest
import sqlite3

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as flask_app


@pytest.fixture(scope='function')
def app():
    """Create and configure a test Flask application instance."""
    # Use a test database with unique name per test
    import time
    test_db_name = f'test_data_{int(time.time() * 1000)}.db'
    flask_app.DB_PATH = os.path.join(os.path.dirname(__file__), test_db_name)
    
    # Clean up any existing test database
    if os.path.exists(flask_app.DB_PATH):
        try:
            os.remove(flask_app.DB_PATH)
        except:
            pass
    
    # Initialize the database
    flask_app.init_db()
    
    # Set testing mode
    flask_app.app.config['TESTING'] = True
    
    yield flask_app.app
    
    # Cleanup: remove test database after tests
    # Give it time to close connections
    import gc
    gc.collect()
    
    try:
        if os.path.exists(flask_app.DB_PATH):
            os.remove(flask_app.DB_PATH)
    except Exception:
        # If we can't delete, at least try to clean it up later
        pass


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask application."""
    return app.test_cli_runner()


def clean_database():
    """Helper function to clean the test database."""
    db_path = os.path.join(os.path.dirname(__file__), 'test_data.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute('DELETE FROM logs')
        conn.commit()
        conn.close()

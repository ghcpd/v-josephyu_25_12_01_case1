"""
Pytest configuration and shared fixtures for Flask Log Management System tests
"""

import pytest
import os
import sys
import sqlite3
import time
from app import app as flask_app, DB_PATH, init_db


@pytest.fixture(autouse=True)
def reset_db_between_tests():
    """Reset database before and after each test"""
    # Clean before test
    attempts = 0
    while os.path.exists(DB_PATH) and attempts < 5:
        try:
            os.remove(DB_PATH)
            break
        except PermissionError:
            attempts += 1
            time.sleep(0.1)
    
    yield
    
    # Clean after test
    attempts = 0
    while os.path.exists(DB_PATH) and attempts < 5:
        try:
            os.remove(DB_PATH)
            break
        except PermissionError:
            attempts += 1
            time.sleep(0.1)


@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing"""
    flask_app.config['TESTING'] = True
    
    # Ensure clean database
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except:
            pass
    
    # Initialize fresh database for this test
    init_db()
    
    yield flask_app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()

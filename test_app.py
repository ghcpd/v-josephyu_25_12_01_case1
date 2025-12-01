import pytest
import json
import os
import sqlite3
from app import app, DB_PATH, init_db


class TestCreateLog:
    """Test POST /logs endpoint"""
    
    def test_create_log_with_valid_level_info(self, client):
        """Test creating a log with valid INFO level"""
        response = client.post('/logs', 
            json={"level": "INFO", "message": "Test message"}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['level'] == 'INFO'
        assert data['message'] == 'Test message'
        assert 'id' in data
        assert 'created_at' in data
    
    def test_create_log_with_debug_level(self, client):
        """Test creating a log with DEBUG level"""
        response = client.post('/logs', 
            json={"level": "DEBUG", "message": "Debug message"}
        )
        assert response.status_code == 201
        assert response.get_json()['level'] == 'DEBUG'
    
    def test_create_log_with_warning_level(self, client):
        """Test creating a log with WARNING level"""
        response = client.post('/logs', 
            json={"level": "WARNING", "message": "Warning message"}
        )
        assert response.status_code == 201
        assert response.get_json()['level'] == 'WARNING'
    
    def test_create_log_with_error_level(self, client):
        """Test creating a log with ERROR level"""
        response = client.post('/logs', 
            json={"level": "ERROR", "message": "Error message"}
        )
        assert response.status_code == 201
        assert response.get_json()['level'] == 'ERROR'
    
    def test_create_log_with_warn_level_should_fail(self, client):
        """Test creating a log with WARN level - should fail per code but docs claim it works"""
        response = client.post('/logs', 
            json={"level": "WARN", "message": "Warning message"}
        )
        # Code only allows WARNING, not WARN - docs are wrong
        assert response.status_code == 400
        assert response.get_json()['error'] == 'invalid level'
    
    def test_create_log_with_context(self, client):
        """Test creating a log with context JSON object"""
        context = {"user": "alice", "request_id": "123"}
        response = client.post('/logs', 
            json={"level": "INFO", "message": "User action", "context": context}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['context'] == context
    
    def test_create_log_with_complex_context(self, client):
        """Test creating a log with complex nested context"""
        context = {
            "user": "alice",
            "metadata": {
                "ip": "192.168.1.1",
                "headers": {"user-agent": "test"}
            },
            "tags": ["prod", "api"]
        }
        response = client.post('/logs', 
            json={"level": "INFO", "message": "Complex context", "context": context}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['context'] == context
    
    def test_create_log_with_null_context(self, client):
        """Test creating a log with null context"""
        response = client.post('/logs', 
            json={"level": "INFO", "message": "No context"}
        )
        assert response.status_code == 201
        assert response.get_json()['context'] is None
    
    def test_create_log_without_context_field(self, client):
        """Test creating a log without context field (optional)"""
        response = client.post('/logs', 
            json={"level": "INFO", "message": "No context"}
        )
        assert response.status_code == 201
        assert response.get_json()['context'] is None
    
    def test_create_log_invalid_level(self, client):
        """Test creating a log with invalid level"""
        response = client.post('/logs', 
            json={"level": "CRITICAL", "message": "Test"}
        )
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_create_log_missing_level(self, client):
        """Test creating a log without level"""
        response = client.post('/logs', 
            json={"message": "Test"}
        )
        assert response.status_code == 400
    
    def test_create_log_missing_message(self, client):
        """Test creating a log without message"""
        response = client.post('/logs', 
            json={"level": "INFO"}
        )
        assert response.status_code == 400
    
    def test_create_log_non_string_message(self, client):
        """Test creating a log with non-string message"""
        response = client.post('/logs', 
            json={"level": "INFO", "message": 123}
        )
        assert response.status_code == 400
        assert response.get_json()['error'] == 'message must be string'
    
    def test_create_log_empty_message(self, client):
        """Test creating a log with empty string message (should be allowed)"""
        response = client.post('/logs', 
            json={"level": "INFO", "message": ""}
        )
        # Empty string is still a valid string
        assert response.status_code == 201


class TestListLogs:
    """Test GET /logs endpoint"""
    
    def test_list_empty_logs(self, client):
        """Test listing logs when none exist"""
        response = client.get('/logs')
        assert response.status_code == 200
        data = response.get_json()
        assert data['items'] == []
        assert data['page'] == 1
        assert data['per_page'] == 10
    
    def test_list_logs_with_data(self, client):
        """Test listing logs after creating some"""
        # Create logs
        client.post('/logs', json={"level": "INFO", "message": "Log 1"})
        client.post('/logs', json={"level": "DEBUG", "message": "Log 2"})
        
        response = client.get('/logs')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 2
    
    def test_list_logs_returns_items_in_descending_order(self, client):
        """Test that logs are returned in descending order by ID"""
        # Create logs
        r1 = client.post('/logs', json={"level": "INFO", "message": "First"})
        id1 = r1.get_json()['id']
        r2 = client.post('/logs', json={"level": "INFO", "message": "Second"})
        id2 = r2.get_json()['id']
        
        response = client.get('/logs')
        data = response.get_json()
        # Should be in descending order (newest first)
        assert data['items'][0]['id'] == id2
        assert data['items'][1]['id'] == id1
    
    def test_list_logs_with_level_filter(self, client):
        """Test listing logs filtered by level"""
        client.post('/logs', json={"level": "INFO", "message": "Info msg"})
        client.post('/logs', json={"level": "DEBUG", "message": "Debug msg"})
        client.post('/logs', json={"level": "INFO", "message": "Info msg 2"})
        
        response = client.get('/logs?level=INFO')
        assert response.status_code == 200
        data = response.get_json()
        # Should only return INFO logs
        assert all(log['level'] == 'INFO' for log in data['items'])
        assert len(data['items']) == 2
    
    def test_list_logs_with_nonexistent_level_filter(self, client):
        """Test listing logs with a level that doesn't exist"""
        client.post('/logs', json={"level": "INFO", "message": "Info msg"})
        
        response = client.get('/logs?level=CRITICAL')
        assert response.status_code == 200
        data = response.get_json()
        assert data['items'] == []  # No logs with CRITICAL level
    
    def test_list_logs_pagination_page_1(self, client):
        """Test pagination with page 1"""
        # Create 5 logs
        for i in range(5):
            client.post('/logs', json={"level": "INFO", "message": f"Log {i}"})
        
        response = client.get('/logs')
        assert response.status_code == 200
        data = response.get_json()
        assert data['page'] == 1
        assert data['per_page'] == 10
        assert len(data['items']) == 5
    
    def test_list_logs_pagination_page_2(self, client):
        """Test pagination with page 2"""
        # Create 15 logs
        for i in range(15):
            client.post('/logs', json={"level": "INFO", "message": f"Log {i}"})
        
        # Get page 2 with default per_page=10
        response = client.get('/logs?page=2')
        assert response.status_code == 200
        data = response.get_json()
        assert data['page'] == 2
        assert data['per_page'] == 10
        assert len(data['items']) == 5  # Only 5 items on page 2
    
    def test_list_logs_custom_per_page(self, client):
        """Test pagination with custom per_page"""
        for i in range(15):
            client.post('/logs', json={"level": "INFO", "message": f"Log {i}"})
        
        response = client.get('/logs?per_page=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data['per_page'] == 5
        assert len(data['items']) == 5
    
    def test_list_logs_per_page_larger_than_total(self, client):
        """Test pagination with per_page larger than total items"""
        for i in range(3):
            client.post('/logs', json={"level": "INFO", "message": f"Log {i}"})
        
        response = client.get('/logs?per_page=20')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 3


class TestDeleteLog:
    """Test DELETE /logs/<id> endpoint"""
    
    def test_delete_existing_log(self, client):
        """Test deleting an existing log"""
        # Create a log
        create_resp = client.post('/logs', json={"level": "INFO", "message": "To delete"})
        log_id = create_resp.get_json()['id']
        
        # Delete it
        response = client.delete(f'/logs/{log_id}')
        assert response.status_code == 204
        
        # Verify it's gone
        list_resp = client.get('/logs')
        assert len(list_resp.get_json()['items']) == 0
    
    def test_delete_non_existent_log(self, client):
        """Test deleting a non-existent log (should not fail per current implementation)"""
        response = client.delete('/logs/999')
        assert response.status_code == 204  # Current implementation always returns 204


class TestExportCSV:
    """Test GET /export endpoint"""
    
    def test_export_csv_endpoint_exists(self, client):
        """Test that /export endpoint works and returns CSV"""
        # Create some logs
        client.post('/logs', json={"level": "INFO", "message": "Log 1"})
        client.post('/logs', json={"level": "ERROR", "message": "Log 2"})
        
        response = client.get('/export')
        assert response.status_code == 200
        assert 'text/csv' in response.content_type or 'attachment' in response.headers.get('Content-Disposition', '')
    
    def test_export_csv_file_created(self, client):
        """Test that CSV file is created in the app directory"""
        client.post('/logs', json={"level": "INFO", "message": "Test"})
        
        # Call export
        response = client.get('/export')
        assert response.status_code == 200
        
        # Check if logs.csv exists in app directory
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs.csv')
        assert os.path.exists(csv_path), "logs.csv should be created in app directory"
    
    def test_export_csv_contains_correct_headers(self, client):
        """Test that CSV file contains correct headers"""
        client.post('/logs', json={"level": "INFO", "message": "Test"})
        
        response = client.get('/export')
        assert response.status_code == 200
        
        # Get the response data
        csv_data = response.get_data(as_text=True)
        lines = csv_data.split('\n')
        headers = lines[0]
        assert 'id' in headers
        assert 'level' in headers
        assert 'message' in headers
        assert 'context' in headers
        assert 'created_at' in headers


class TestDBLocationConstraint:
    """Test that database is created in app directory"""
    
    def test_db_file_location(self, app):
        """Verify data.db is in the application directory (same folder as app.py)"""
        app_dir = os.path.dirname(__file__)
        expected_db_path = os.path.join(app_dir, 'data.db')
        assert os.path.exists(expected_db_path), f"Database should be at {expected_db_path}"
        assert os.path.isabs(DB_PATH), "DB_PATH should be absolute"


class TestContextPersistence:
    """Test that context is properly stored and retrieved"""
    
    def test_context_stored_as_json_string(self, client):
        """Verify context is stored as JSON but retrieved as object"""
        context = {"key": "value", "nested": {"a": 1}}
        
        response = client.post('/logs',
            json={"level": "INFO", "message": "Test", "context": context}
        )
        assert response.status_code == 201
        
        # Retrieve and verify
        list_response = client.get('/logs')
        items = list_response.get_json()['items']
        assert items[0]['context'] == context
    
    def test_empty_context_object(self, client):
        """Test creating log with empty context object"""
        response = client.post('/logs',
            json={"level": "INFO", "message": "Test", "context": {}}
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data['context'] == {}


class TestListLogs:
    """Test GET /logs endpoint"""
    
    def test_list_empty_logs(self, client):
        """Test listing logs when none exist"""
        response = client.get('/logs')
        assert response.status_code == 200
        data = response.get_json()
        assert data['items'] == []
        assert data['page'] == 1
        assert data['per_page'] == 10
    
    def test_list_logs_with_data(self, client):
        """Test listing logs after creating some"""
        # Create logs
        client.post('/logs', json={"level": "INFO", "message": "Log 1"})
        client.post('/logs', json={"level": "DEBUG", "message": "Log 2"})
        
        response = client.get('/logs')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['items']) == 2
    
    def test_list_logs_with_level_filter(self, client):
        """Test listing logs filtered by level"""
        client.post('/logs', json={"level": "INFO", "message": "Info msg"})
        client.post('/logs', json={"level": "DEBUG", "message": "Debug msg"})
        client.post('/logs', json={"level": "INFO", "message": "Info msg 2"})
        
        response = client.get('/logs?level=INFO')
        assert response.status_code == 200
        data = response.get_json()
        # Should only return INFO logs
        assert all(log['level'] == 'INFO' for log in data['items'])
    
    def test_list_logs_pagination_page_2(self, client):
        """Test pagination with page 2"""
        # Create 15 logs
        for i in range(15):
            client.post('/logs', json={"level": "INFO", "message": f"Log {i}"})
        
        # Get page 2 with default per_page=10
        response = client.get('/logs?page=2')
        assert response.status_code == 200
        data = response.get_json()
        assert data['page'] == 2
        assert data['per_page'] == 10
        assert len(data['items']) == 5  # Only 5 items on page 2
    
    def test_list_logs_custom_per_page(self, client):
        """Test pagination with custom per_page"""
        for i in range(15):
            client.post('/logs', json={"level": "INFO", "message": f"Log {i}"})
        
        response = client.get('/logs?per_page=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data['per_page'] == 5
        assert len(data['items']) == 5


class TestDeleteLog:
    """Test DELETE /logs/<id> endpoint"""
    
    def test_delete_existing_log(self, client):
        """Test deleting an existing log"""
        # Create a log
        create_resp = client.post('/logs', json={"level": "INFO", "message": "To delete"})
        log_id = create_resp.get_json()['id']
        
        # Delete it
        response = client.delete(f'/logs/{log_id}')
        assert response.status_code == 204
        
        # Verify it's gone
        list_resp = client.get('/logs')
        assert len(list_resp.get_json()['items']) == 0
    
    def test_delete_non_existent_log(self, client):
        """Test deleting a non-existent log (should not fail per current implementation)"""
        response = client.delete('/logs/999')
        assert response.status_code == 204  # Current implementation always returns 204


class TestExportCSV:
    """Test GET /export endpoint"""
    
    def test_export_csv_endpoint_exists(self, client):
        """Test that /export endpoint works and returns CSV"""
        # Create some logs
        client.post('/logs', json={"level": "INFO", "message": "Log 1"})
        client.post('/logs', json={"level": "ERROR", "message": "Log 2"})
        
        response = client.get('/export')
        assert response.status_code == 200
        assert 'text/csv' in response.content_type or 'attachment' in response.headers.get('Content-Disposition', '')
    
    def test_export_csv_file_created(self, client):
        """Test that CSV file is created in the app directory"""
        client.post('/logs', json={"level": "INFO", "message": "Test"})
        
        # Call export
        response = client.get('/export')
        assert response.status_code == 200
        
        # Check if logs.csv exists in app directory
        csv_path = os.path.join(os.path.dirname(__file__), 'logs.csv')
        assert os.path.exists(csv_path), "logs.csv should be created in app directory"


class TestDBLocationConstraint:
    """Test that database is created in app directory"""
    
    def test_db_file_location(self, client):
        """Verify data.db is in the application directory (same folder as app.py)"""
        app_dir = os.path.dirname(__file__)
        expected_db_path = os.path.join(app_dir, 'data.db')
        assert os.path.exists(expected_db_path), f"Database should be at {expected_db_path}"
        assert os.path.isabs(DB_PATH), "DB_PATH should be absolute"

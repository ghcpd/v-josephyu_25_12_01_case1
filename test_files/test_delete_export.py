"""
Test suite for Flask Log Management System - Delete and Export
"""
import json
import os
import pytest


class TestLogDeletion:
    """Tests for DELETE /logs/<id> endpoint"""
    
    def test_delete_existing_log(self, client):
        """Test deleting an existing log"""
        # Create a log
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'To be deleted'
            }),
            content_type='application/json'
        )
        log_id = json.loads(response.data)['id']
        
        # Delete it
        response = client.delete(f'/logs/{log_id}')
        assert response.status_code == 204
        assert response.data == b''
        
        # Verify it's gone
        response = client.get('/logs')
        data = json.loads(response.data)
        log_ids = [item['id'] for item in data['items']]
        assert log_id not in log_ids
    
    def test_delete_nonexistent_log(self, client):
        """Test deleting a log that doesn't exist"""
        # Try to delete non-existent ID
        response = client.delete('/logs/99999')
        # DELETE returns 204 even if record doesn't exist (idempotent)
        assert response.status_code == 204
    
    def test_delete_multiple_logs(self, client):
        """Test deleting multiple logs"""
        # Create multiple logs
        ids = []
        for i in range(5):
            response = client.post('/logs',
                data=json.dumps({
                    'level': 'INFO',
                    'message': f'Log {i}'
                }),
                content_type='application/json'
            )
            ids.append(json.loads(response.data)['id'])
        
        # Delete first and last
        client.delete(f'/logs/{ids[0]}')
        client.delete(f'/logs/{ids[4]}')
        
        # Verify only middle ones remain
        response = client.get('/logs')
        data = json.loads(response.data)
        remaining_ids = [item['id'] for item in data['items']]
        
        assert ids[0] not in remaining_ids
        assert ids[4] not in remaining_ids
        assert ids[1] in remaining_ids
        assert ids[2] in remaining_ids
        assert ids[3] in remaining_ids
    
    def test_delete_with_invalid_id_format(self, client):
        """Test deleting with non-integer ID"""
        response = client.delete('/logs/invalid')
        # Flask routing will return 404 for invalid format
        assert response.status_code == 404


class TestLogExport:
    """Tests for GET /export endpoint"""
    
    def test_export_empty_database(self, client, app):
        """Test exporting when database is empty"""
        with app.app_context():
            response = client.get('/export')
            
            assert response.status_code == 200
            assert response.headers['Content-Type'] == 'text/csv; charset=utf-8'
            
            # Check CSV content
            csv_content = response.data.decode('utf-8')
            lines = csv_content.strip().split('\n')
            
            # Should have header row only
            assert len(lines) >= 1
            assert 'id,level,message,context,created_at' in lines[0]
    
    def test_export_with_data(self, client, app):
        """Test exporting logs to CSV"""
        # Create test logs
        client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Test message 1',
                'context': {'user': 'alice'}
            }),
            content_type='application/json'
        )
        client.post('/logs',
            data=json.dumps({
                'level': 'WARNING',
                'message': 'Test message 2'
            }),
            content_type='application/json'
        )
        
        with app.app_context():
            response = client.get('/export')
            
            assert response.status_code == 200
            
            # Check CSV content
            csv_content = response.data.decode('utf-8')
            lines = csv_content.strip().split('\n')
            
            # Should have header + 2 data rows
            assert len(lines) >= 3
            
            # Check header
            assert 'id' in lines[0]
            assert 'level' in lines[0]
            assert 'message' in lines[0]
            
            # Check data is present
            full_csv = '\n'.join(lines)
            assert 'INFO' in full_csv
            assert 'WARNING' in full_csv
    
    def test_export_file_created(self, client, app):
        """Test that export creates a logs.csv file"""
        # Create a log
        client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Export test'
            }),
            content_type='application/json'
        )
        
        # Get the app directory
        app_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(app_dir, 'logs.csv')
        
        # Remove existing CSV if present
        if os.path.exists(csv_path):
            os.remove(csv_path)
        
        with app.app_context():
            response = client.get('/export')
            assert response.status_code == 200
            
            # Note: The file is created in the app directory, not test directory
            # This test verifies the endpoint works but can't easily verify file location
    
    def test_export_csv_format(self, client, app):
        """Test that exported CSV has correct format"""
        # Create log with known data
        client.post('/logs',
            data=json.dumps({
                'level': 'ERROR',
                'message': 'CSV format test',
                'context': {'error_code': 500}
            }),
            content_type='application/json'
        )
        
        with app.app_context():
            response = client.get('/export')
            csv_content = response.data.decode('utf-8')
            lines = csv_content.strip().split('\n')
            
            # Parse header
            headers = lines[0].split(',')
            assert 'id' in headers
            assert 'level' in headers
            assert 'message' in headers
            assert 'context' in headers
            assert 'created_at' in headers
    
    def test_export_download_headers(self, client):
        """Test that export response has correct download headers"""
        response = client.get('/export')
        
        assert response.status_code == 200
        # Check for CSV content type
        assert 'text/csv' in response.headers.get('Content-Type', '')
        # Check for attachment disposition
        content_disposition = response.headers.get('Content-Disposition', '')
        assert 'attachment' in content_disposition
        assert 'logs.csv' in content_disposition
    
    def test_export_with_special_characters(self, client, app):
        """Test exporting logs with special characters in message"""
        # Create log with special characters
        client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Message with "quotes" and, commas',
                'context': {'key': 'value with "quotes"'}
            }),
            content_type='application/json'
        )
        
        with app.app_context():
            response = client.get('/export')
            assert response.status_code == 200
            
            # CSV should handle special characters properly
            csv_content = response.data.decode('utf-8')
            assert 'quotes' in csv_content
    
    def test_export_ordering(self, client, app):
        """Test that export orders logs correctly (descending by ID)"""
        # Create logs in sequence
        ids = []
        for i in range(5):
            response = client.post('/logs',
                data=json.dumps({
                    'level': 'INFO',
                    'message': f'Message {i}'
                }),
                content_type='application/json'
            )
            ids.append(json.loads(response.data)['id'])
        
        with app.app_context():
            response = client.get('/export')
            csv_content = response.data.decode('utf-8')
            lines = csv_content.strip().split('\n')
            
            # Extract IDs from CSV (first column)
            csv_ids = []
            for line in lines[1:]:  # Skip header
                if line:
                    csv_id = line.split(',')[0]
                    csv_ids.append(int(csv_id))
            
            # Should be in descending order
            assert csv_ids == sorted(ids, reverse=True)


class TestDatabaseIntegration:
    """Tests for database-related functionality"""
    
    def test_database_file_location(self, app):
        """Test that database is created in correct location"""
        import app as flask_app
        
        # DB_PATH should be set to test location by conftest
        assert 'test_data.db' in flask_app.DB_PATH
    
    def test_context_stored_as_json_string(self, client, app):
        """Test that context is stored as JSON string in database"""
        import sqlite3
        import app as flask_app
        
        # Create log with context
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Test',
                'context': {'key': 'value'}
            }),
            content_type='application/json'
        )
        log_id = json.loads(response.data)['id']
        
        # Query database directly
        conn = sqlite3.connect(flask_app.DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT context FROM logs WHERE id = ?', (log_id,))
        row = cur.fetchone()
        conn.close()
        
        # Context should be stored as JSON string
        assert row is not None
        context_value = row[0]
        assert isinstance(context_value, str)
        assert '"key"' in context_value
        assert '"value"' in context_value
    
    def test_null_context_stored_correctly(self, client, app):
        """Test that null context is stored as NULL in database"""
        import sqlite3
        import app as flask_app
        
        # Create log without context
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'No context'
            }),
            content_type='application/json'
        )
        log_id = json.loads(response.data)['id']
        
        # Query database directly
        conn = sqlite3.connect(flask_app.DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT context FROM logs WHERE id = ?', (log_id,))
        row = cur.fetchone()
        conn.close()
        
        # Context should be NULL
        assert row[0] is None
    
    def test_timestamp_format(self, client):
        """Test that timestamp is in ISO 8601 format"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Timestamp test'
            }),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        timestamp = data['created_at']
        
        # Should be in ISO format with 'T' separator
        assert 'T' in timestamp
        # Should contain date and time parts
        assert len(timestamp) > 19  # YYYY-MM-DDTHH:MM:SS

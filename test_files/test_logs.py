"""
Test suite for Flask Log Management System - Log Creation and Retrieval
"""
import json
import pytest


class TestLogCreation:
    """Tests for POST /logs endpoint"""
    
    def test_create_log_with_all_fields(self, client):
        """Test creating a log with level, message, and context"""
        response = client.post('/logs', 
            data=json.dumps({
                'level': 'INFO',
                'message': 'Test message',
                'context': {'user': 'alice', 'action': 'login'}
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['level'] == 'INFO'
        assert data['message'] == 'Test message'
        assert data['context'] == {'user': 'alice', 'action': 'login'}
        assert 'id' in data
        assert 'created_at' in data
    
    def test_create_log_without_context(self, client):
        """Test creating a log without context field"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'DEBUG',
                'message': 'Debug message'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['level'] == 'DEBUG'
        assert data['message'] == 'Debug message'
        assert data['context'] is None
    
    def test_create_log_with_null_context(self, client):
        """Test creating a log with null context"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'WARNING',
                'message': 'Warning message',
                'context': None
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['context'] is None
    
    def test_create_log_with_all_valid_levels(self, client):
        """Test creating logs with all valid level values"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        
        for level in valid_levels:
            response = client.post('/logs',
                data=json.dumps({
                    'level': level,
                    'message': f'Test {level} message'
                }),
                content_type='application/json'
            )
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['level'] == level
    
    def test_create_log_with_invalid_level(self, client):
        """Test that invalid level returns 400 error"""
        # Test with documented but incorrect "WARN" level
        response = client.post('/logs',
            data=json.dumps({
                'level': 'WARN',
                'message': 'Test message'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'invalid level'
    
    def test_create_log_with_invalid_level_variations(self, client):
        """Test various invalid level values"""
        invalid_levels = ['CRITICAL', 'FATAL', 'TRACE', 'warn', 'info']
        
        for level in invalid_levels:
            response = client.post('/logs',
                data=json.dumps({
                    'level': level,
                    'message': 'Test message'
                }),
                content_type='application/json'
            )
            assert response.status_code == 400
    
    def test_create_log_without_message(self, client):
        """Test that missing message field causes error"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO'
            }),
            content_type='application/json'
        )
        
        # Should fail validation
        assert response.status_code == 400 or response.status_code == 500
    
    def test_create_log_with_non_string_message(self, client):
        """Test that non-string message returns error"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 123
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_create_log_with_complex_context(self, client):
        """Test creating log with nested context object"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'ERROR',
                'message': 'Complex error',
                'context': {
                    'error': {
                        'type': 'DatabaseError',
                        'details': {
                            'table': 'users',
                            'operation': 'INSERT'
                        }
                    },
                    'timestamp': '2025-12-01T00:00:00'
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert isinstance(data['context'], dict)
        assert 'error' in data['context']


class TestLogRetrieval:
    """Tests for GET /logs endpoint"""
    
    def test_list_empty_logs(self, client):
        """Test listing logs when database is empty"""
        response = client.get('/logs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
        assert isinstance(data['items'], list)
        assert len(data['items']) == 0
        assert data['page'] == 1
        assert data['per_page'] == 10
    
    def test_list_logs_with_data(self, client):
        """Test listing logs after creating some"""
        # Create test logs
        for i in range(3):
            client.post('/logs',
                data=json.dumps({
                    'level': 'INFO',
                    'message': f'Test message {i}'
                }),
                content_type='application/json'
            )
        
        response = client.get('/logs')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 3
    
    def test_list_logs_pagination(self, client):
        """Test pagination parameters"""
        # Create 15 test logs
        for i in range(15):
            client.post('/logs',
                data=json.dumps({
                    'level': 'INFO',
                    'message': f'Log {i}'
                }),
                content_type='application/json'
            )
        
        # Test first page with 5 items
        response = client.get('/logs?page=1&per_page=5')
        data = json.loads(response.data)
        assert len(data['items']) == 5
        assert data['page'] == 1
        assert data['per_page'] == 5
        
        # Test second page
        response = client.get('/logs?page=2&per_page=5')
        data = json.loads(response.data)
        assert len(data['items']) == 5
        assert data['page'] == 2
        
        # Test third page
        response = client.get('/logs?page=3&per_page=5')
        data = json.loads(response.data)
        assert len(data['items']) == 5
    
    def test_list_logs_default_pagination(self, client):
        """Test that default pagination values are correct"""
        response = client.get('/logs')
        data = json.loads(response.data)
        assert data['page'] == 1
        assert data['per_page'] == 10
    
    def test_list_logs_filter_by_level(self, client):
        """Test filtering logs by level"""
        # Create logs with different levels
        client.post('/logs', data=json.dumps({'level': 'INFO', 'message': 'Info 1'}), content_type='application/json')
        client.post('/logs', data=json.dumps({'level': 'WARNING', 'message': 'Warning 1'}), content_type='application/json')
        client.post('/logs', data=json.dumps({'level': 'ERROR', 'message': 'Error 1'}), content_type='application/json')
        client.post('/logs', data=json.dumps({'level': 'INFO', 'message': 'Info 2'}), content_type='application/json')
        
        # Filter by INFO
        response = client.get('/logs?level=INFO')
        data = json.loads(response.data)
        assert len(data['items']) == 2
        for item in data['items']:
            assert item['level'] == 'INFO'
        
        # Filter by WARNING
        response = client.get('/logs?level=WARNING')
        data = json.loads(response.data)
        assert len(data['items']) == 1
        assert data['items'][0]['level'] == 'WARNING'
    
    def test_list_logs_order(self, client):
        """Test that logs are returned in descending order by ID"""
        # Create logs
        ids = []
        for i in range(5):
            response = client.post('/logs',
                data=json.dumps({
                    'level': 'INFO',
                    'message': f'Message {i}'
                }),
                content_type='application/json'
            )
            data = json.loads(response.data)
            ids.append(data['id'])
        
        # Get logs
        response = client.get('/logs')
        data = json.loads(response.data)
        
        # Check they're in descending order
        returned_ids = [item['id'] for item in data['items']]
        assert returned_ids == sorted(ids, reverse=True)
    
    def test_list_logs_context_deserialization(self, client):
        """Test that context is properly deserialized in list response"""
        # Create log with context
        client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Test',
                'context': {'key': 'value', 'number': 42}
            }),
            content_type='application/json'
        )
        
        # Retrieve and check context
        response = client.get('/logs')
        data = json.loads(response.data)
        assert len(data['items']) > 0
        item = data['items'][0]
        assert isinstance(item['context'], dict)
        assert item['context']['key'] == 'value'
        assert item['context']['number'] == 42

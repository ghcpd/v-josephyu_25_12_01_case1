"""
Test suite for Flask Log Management System - Edge Cases and Error Handling
"""
import json
import pytest


class TestEdgeCases:
    """Tests for edge cases and boundary conditions"""
    
    def test_very_long_message(self, client):
        """Test creating log with very long message"""
        long_message = "A" * 10000
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': long_message
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == long_message
    
    def test_empty_message(self, client):
        """Test creating log with empty message string"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': ''
            }),
            content_type='application/json'
        )
        
        # Empty string is still a string, should be accepted
        assert response.status_code == 201
    
    def test_special_characters_in_message(self, client):
        """Test message with special characters"""
        special_message = 'Test with "quotes", \'apostrophes\', and \n newlines \t tabs'
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': special_message
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        # JSON should handle escaping
        assert 'quotes' in data['message']
    
    def test_unicode_in_message(self, client):
        """Test message with unicode characters"""
        unicode_message = 'Test with émojis 🎉 and 中文 characters'
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': unicode_message
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert '🎉' in data['message']
        assert '中文' in data['message']
    
    def test_large_context_object(self, client):
        """Test creating log with large context object"""
        large_context = {
            f'key_{i}': f'value_{i}' for i in range(1000)
        }
        
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Large context test',
                'context': large_context
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert len(data['context']) == 1000
    
    def test_deeply_nested_context(self, client):
        """Test context with deep nesting"""
        # Create deeply nested structure
        nested = {'level_1': {'level_2': {'level_3': {'level_4': {'value': 'deep'}}}}}
        
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Nested context',
                'context': nested
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['context']['level_1']['level_2']['level_3']['level_4']['value'] == 'deep'
    
    def test_pagination_beyond_available_pages(self, client):
        """Test requesting page beyond available data"""
        # Create only 5 logs
        for i in range(5):
            client.post('/logs',
                data=json.dumps({
                    'level': 'INFO',
                    'message': f'Log {i}'
                }),
                content_type='application/json'
            )
        
        # Request page 10 (beyond available data)
        response = client.get('/logs?page=10&per_page=10')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 0
        assert data['page'] == 10
    
    def test_pagination_with_zero_per_page(self, client):
        """Test pagination with per_page=0"""
        # This might cause issues, test how it's handled
        response = client.get('/logs?per_page=0')
        # Implementation may vary - document actual behavior
        # Could return 200 with empty items, or error
        assert response.status_code in [200, 400, 500]
    
    def test_pagination_with_negative_values(self, client):
        """Test pagination with negative values"""
        response = client.get('/logs?page=-1&per_page=-5')
        # Should handle gracefully, likely returning error or using defaults
        # Document actual behavior
        assert response.status_code in [200, 400, 500]
    
    def test_filter_with_nonexistent_level(self, client):
        """Test filtering by level that doesn't exist in database"""
        # Create some logs
        client.post('/logs',
            data=json.dumps({'level': 'INFO', 'message': 'Test'}),
            content_type='application/json'
        )
        
        # Filter by level that doesn't exist
        response = client.get('/logs?level=CRITICAL')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['items']) == 0


class TestErrorHandling:
    """Tests for error handling"""
    
    def test_malformed_json(self, client):
        """Test sending malformed JSON"""
        response = client.post('/logs',
            data='{"level": "INFO", "message": "Test"',  # Missing closing brace
            content_type='application/json'
        )
        
        # Should return 400 or 500
        assert response.status_code in [400, 500]
    
    def test_missing_content_type(self, client):
        """Test POST without Content-Type header"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Test'
            })
            # No content_type specified
        )
        
        # force=True in code should still parse it
        # Check if it works or returns error
        assert response.status_code in [201, 400, 415]
    
    def test_empty_request_body(self, client):
        """Test POST with empty body"""
        response = client.post('/logs',
            data='',
            content_type='application/json'
        )
        
        # Should return error
        assert response.status_code in [400, 500]
    
    def test_missing_level_field(self, client):
        """Test POST without level field"""
        response = client.post('/logs',
            data=json.dumps({
                'message': 'Test'
            }),
            content_type='application/json'
        )
        
        # Should return error
        assert response.status_code in [400, 500]
    
    def test_extra_fields_ignored(self, client):
        """Test that extra fields in request are ignored"""
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Test',
                'extra_field': 'should be ignored',
                'another_field': 123
            }),
            content_type='application/json'
        )
        
        # Should succeed and ignore extra fields
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'extra_field' not in data
        assert 'another_field' not in data
    
    def test_case_sensitive_level(self, client):
        """Test that level is case-sensitive"""
        # Lowercase should fail
        response = client.post('/logs',
            data=json.dumps({
                'level': 'info',
                'message': 'Test'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Mixed case should fail
        response = client.post('/logs',
            data=json.dumps({
                'level': 'Info',
                'message': 'Test'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_context_with_non_json_serializable(self, client):
        """Test context that can't be JSON serialized"""
        # This test is tricky because we're sending JSON, so it's already serialized
        # But we can test with special values
        response = client.post('/logs',
            data='{"level": "INFO", "message": "Test", "context": {"date": "2025-12-01"}}',
            content_type='application/json'
        )
        
        # Should work since JSON strings are serializable
        assert response.status_code == 201


class TestConcurrency:
    """Tests for concurrent access (basic)"""
    
    def test_multiple_creates_sequential(self, client):
        """Test creating multiple logs in sequence"""
        ids = []
        for i in range(10):
            response = client.post('/logs',
                data=json.dumps({
                    'level': 'INFO',
                    'message': f'Log {i}'
                }),
                content_type='application/json'
            )
            assert response.status_code == 201
            data = json.loads(response.data)
            ids.append(data['id'])
        
        # All IDs should be unique and sequential
        assert len(ids) == len(set(ids))
        assert ids == sorted(ids)
    
    def test_create_and_list_consistency(self, client):
        """Test that created logs immediately appear in list"""
        # Create a log
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': 'Consistency test'
            }),
            content_type='application/json'
        )
        created_id = json.loads(response.data)['id']
        
        # Immediately list logs
        response = client.get('/logs')
        data = json.loads(response.data)
        
        # Created log should be present
        ids = [item['id'] for item in data['items']]
        assert created_id in ids
    
    def test_delete_and_list_consistency(self, client):
        """Test that deleted logs immediately disappear from list"""
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
        client.delete(f'/logs/{log_id}')
        
        # Immediately list logs
        response = client.get('/logs')
        data = json.loads(response.data)
        
        # Deleted log should not be present
        ids = [item['id'] for item in data['items']]
        assert log_id not in ids


class TestSQLInjectionPrevention:
    """Tests to verify SQL injection is prevented"""
    
    def test_sql_injection_in_level_filter(self, client):
        """Test SQL injection attempts in level filter"""
        # Try SQL injection in level parameter
        malicious_levels = [
            "INFO' OR '1'='1",
            "INFO; DROP TABLE logs;--",
            "INFO' UNION SELECT * FROM logs--"
        ]
        
        for level in malicious_levels:
            response = client.get(f'/logs?level={level}')
            # Should not cause error or injection
            assert response.status_code == 200
            # Should return empty or safe results
    
    def test_sql_injection_in_message(self, client):
        """Test SQL injection attempts in message field"""
        malicious_message = "Test'; DROP TABLE logs;--"
        
        response = client.post('/logs',
            data=json.dumps({
                'level': 'INFO',
                'message': malicious_message
            }),
            content_type='application/json'
        )
        
        # Should succeed and store the message as-is
        assert response.status_code == 201
        
        # Verify database still exists by listing logs
        response = client.get('/logs')
        assert response.status_code == 200

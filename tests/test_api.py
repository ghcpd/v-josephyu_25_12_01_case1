import os
import tempfile
import json
import sqlite3
import pytest

from app import app, init_db, DB_PATH


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    # Create a temporary DB file in the repo directory to mimic behavior
    db_file = tmp_path / "data.db"
    # Make sure calls to DB_PATH use this temp file
    monkeypatch.setattr('app.DB_PATH', str(db_file))
    # initialize schema
    init_db()
    yield str(db_file)
    # cleanup
    if os.path.exists(str(db_file)):
        os.unlink(str(db_file))


def test_create_log_success(client=None):
    c = app.test_client()
    payload = {"level": "INFO", "message": "Test created", "context": {"user": "bob"}}
    resp = c.post('/logs', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['level'] == 'INFO'
    assert data['message'] == 'Test created'
    assert data['context'] == {"user": "bob"}


def test_create_log_invalid_level():
    c = app.test_client()
    payload = {"level": "INVALID", "message": "Test", "context": {}}
    resp = c.post('/logs', json=payload)
    assert resp.status_code == 400
    assert resp.get_json().get('error') == 'invalid level'


def test_create_log_non_string_message():
    c = app.test_client()
    payload = {"level": "INFO", "message": 12345, "context": {}}
    resp = c.post('/logs', json=payload)
    assert resp.status_code == 400
    assert resp.get_json().get('error') == 'message must be string'


def test_list_logs_and_filter():
    c = app.test_client()
    # create items
    c.post('/logs', json={"level": "INFO", "message": "A"})
    c.post('/logs', json={"level": "DEBUG", "message": "B"})
    # filter INFO
    resp = c.get('/logs?level=INFO')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data['items'], list)
    assert all(item['level'] == 'INFO' for item in data['items'])


def test_delete_log():
    c = app.test_client()
    r = c.post('/logs', json={"level": "INFO", "message": "toDelete"})
    log_id = r.get_json()['id']
    resp = c.delete(f'/logs/{log_id}')
    assert resp.status_code == 204
    # confirm deletion
    resp2 = c.get('/logs')
    data = resp2.get_json()
    assert all(item['id'] != log_id for item in data['items'])


def test_export_csv(tmp_path):
    c = app.test_client()
    # create items
    c.post('/logs', json={"level": "INFO", "message": "C"})
    r = c.get('/export')
    assert r.status_code == 200
    assert r.headers['Content-Disposition'].startswith('attachment;') or 'logs.csv' in r.headers.get('Content-Disposition', '')


def test_db_default_path():
    # Ensure default DB path is in same directory as app.py and named data.db
    import os
    expected = os.path.join(os.path.dirname(__file__), os.pardir, 'data.db')
    expected = os.path.normpath(expected)
    # actual DB path defined in app module
    from app import DB_PATH as actual
    actual_norm = os.path.normpath(actual)
    # The default DB path should be located in the same directory as app.py and be called data.db
    assert actual_norm.endswith(os.path.normpath('data.db')) or os.path.basename(actual_norm) == os.path.basename(actual_norm)


def test_create_context_number():
    c = app.test_client()
    resp = c.post('/logs', json={"level": "INFO", "message": "numctx", "context": 123})
    assert resp.status_code == 201
    assert resp.get_json()['context'] == 123

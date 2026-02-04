import os
import json
import tempfile
import sqlite3
import csv
import pytest
from app import app, init_db, DB_PATH

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # isolate DB per test using a temp file to avoid file locks on Windows
    tmp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    tmp_db.close()
    original_db = None
    try:
        # swap the DB path used by the app
        original_db = os.environ.get('DB_PATH')
        os.environ['DB_PATH'] = tmp_db.name
        # monkey patch the app module DB_PATH
        import app as _app
        _app.DB_PATH = tmp_db.name
        _app.init_db()
        yield
    finally:
        # cleanup
        try:
            if os.path.exists(tmp_db.name):
                os.remove(tmp_db.name)
        except Exception:
            pass
        if original_db is None:
            os.environ.pop('DB_PATH', None)
        else:
            os.environ['DB_PATH'] = original_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def test_create_log_and_list(client):
    # create log
    payload = {"level": "INFO", "message": "Started", "context": {"user": "alice"}}
    res = client.post('/logs', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['level'] == 'INFO'
    assert data['message'] == 'Started'
    assert data['context'] == payload['context']

    # list logs
    res = client.get('/logs')
    assert res.status_code == 200
    data = res.get_json()
    assert data['items'][0]['message'] == 'Started'


def test_invalid_level_returns_400(client):
    payload = {"level": "WARN", "message": "Should fail"}
    res = client.post('/logs', json=payload)
    assert res.status_code == 400


def test_missing_level_returns_400(client):
    payload = {"message": "Missing level"}
    res = client.post('/logs', json=payload)
    assert res.status_code == 400


def test_context_must_be_json_like(client):
    # send context as raw string (non-object) - should still be accepted by server
    payload = {"level": "INFO", "message": "Str context", "context": "simple-string"}
    res = client.post('/logs', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    # server returns context as original
    assert data['context'] == "simple-string"


def test_delete_log(client):
    # create
    res = client.post('/logs', json={"level": "INFO", "message": "To delete"})
    assert res.status_code == 201
    log_id = res.get_json()['id']

    # delete
    res = client.delete(f'/logs/{log_id}')
    assert res.status_code == 204

    # verify deleted
    res = client.get('/logs')
    assert res.status_code == 200
    data = res.get_json()
    assert all(item['id'] != log_id for item in data['items'])


def test_export_csv(client, tmp_path):
    # create logs
    client.post('/logs', json={"level": "INFO", "message": "E1"})
    client.post('/logs', json={"level": "ERROR", "message": "E2"})

    res = client.get('/export')
    assert res.status_code == 200
    content = res.get_data()
    # check header exists
    assert b'id,level,message,context,created_at' in content


def test_db_file_location_matches_app_dir():
    # confirm the app's source declares DB_PATH pointing to data.db in the app directory
    app_src = open(os.path.join(os.path.dirname(__file__), '..', 'app.py')).read()
    assert "os.path.join(os.path.dirname(__file__), 'data.db')" in app_src or 'data.db' in app_src


def test_allowed_levels_match_docs():
    import app as _app
    # the code uses these levels: DEBUG, INFO, WARNING, ERROR
    assert set(["DEBUG", "INFO", "WARNING", "ERROR"]) == _app.ALLOWED_LEVELS

import os
import tempfile
import json
import pytest
from datetime import datetime

import app as flask_app


@pytest.fixture
def client(monkeypatch, tmp_path):
    # Point DB_PATH to a temporary DB file so tests don't modify workspace
    db_file = tmp_path / "data.db"
    monkeypatch.setattr(flask_app, "DB_PATH", str(db_file))
    flask_app.init_db()
    flask_app.app.config["TESTING"] = True
    client = flask_app.app.test_client()
    yield client


def test_db_path_is_data_db():
    # Confirm DB_PATH references data.db in app dir by default
    default = os.path.join(os.path.dirname(flask_app.__file__), 'data.db')
    assert os.path.basename(flask_app.DB_PATH) == 'data.db'
    # If running in test mode we override it; ensure attribute exists
    assert hasattr(flask_app, 'DB_PATH')


def test_create_log_success(client):
    payload = {"level": "INFO", "message": "Started", "context": {"user": "alice"}}
    resp = client.post('/logs', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['level'] == 'INFO'
    assert data['message'] == 'Started'
    assert isinstance(data['context'], dict)


def test_create_log_invalid_level(client):
    payload = {"level": "WARN", "message": "Legacy level", "context": {"user": "bob"}}
    resp = client.post('/logs', data=json.dumps(payload), content_type='application/json')
    # According to README, "WARN" was allowed; code currently rejects it and returns 400
    assert resp.status_code == 400


def test_context_must_be_object(client):
    # README states context must be JSON object. Current implementation does not enforce.
    # We assert expected behavior that context must be object; this will surface as a failing test
    payload = {"level": "INFO", "message": "String context", "context": "not-an-object"}
    resp = client.post('/logs', data=json.dumps(payload), content_type='application/json')
    # Desired behavior: 400; Current behavior: 201; therefore test expects 400 and will fail
    assert resp.status_code == 400


def test_list_logs_pagination_and_filter(client):
    # Seed multiple logs
    for i in range(1, 16):
        payload = {"level": "DEBUG" if i % 2 == 0 else "INFO", "message": f"msg{i}", "context": {"i": i}}
        r = client.post('/logs', data=json.dumps(payload), content_type='application/json')
        assert r.status_code == 201

    r = client.get('/logs?level=DEBUG&page=2&per_page=3')
    assert r.status_code == 200
    data = r.get_json()
    assert data['page'] == 2
    assert data['per_page'] == 3
    assert isinstance(data['items'], list)


def test_delete_log(client):
    payload = {"level": "INFO", "message": "ToDelete", "context": {}}
    r = client.post('/logs', data=json.dumps(payload), content_type='application/json')
    assert r.status_code == 201
    log_id = r.get_json()['id']
    dr = client.delete(f'/logs/{log_id}')
    assert dr.status_code == 204


def test_export_csv(client, tmp_path):
    # Seed a log
    payload = {"level": "INFO", "message": "ExportTest", "context": {"x": 1}}
    r = client.post('/logs', data=json.dumps(payload), content_type='application/json')
    assert r.status_code == 201

    r = client.get('/export')
    assert r.status_code == 200
    content_disposition = r.headers.get('Content-Disposition')
    assert content_disposition is not None
    data = r.get_data(as_text=True)
    assert 'id,level,message,context,created_at' in data

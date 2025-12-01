import os
import tempfile
import json
import pytest
from app import app, init_db


@pytest.fixture(autouse=True)
def _tmp_db(tmp_path, monkeypatch):
    db_path = tmp_path / 'data.db'
    monkeypatch.setattr('app.DB_PATH', str(db_path))
    init_db()
    yield


def test_v1_create_and_list():
    c = app.test_client()
    r = c.post('/logs', json={'level': 'INFO', 'message': 'ok', 'context': {'a': 1}})
    assert r.status_code == 201
    list_resp = c.get('/logs')
    assert list_resp.status_code == 200
    assert len(list_resp.get_json()['items']) >= 1

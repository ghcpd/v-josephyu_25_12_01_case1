import os
import json
import sqlite3
import pytest

import app as log_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client with an isolated temporary database."""
    db_path = tmp_path / "data.db"
    monkeypatch.setattr(log_app, "DB_PATH", str(db_path))
    log_app.init_db()

    # Ensure export writes to temp directory by monkeypatching __file__ dirname reference
    # We simulate app directory as tmp_path for export path resolution.
    monkeypatch.setattr(log_app, "__file__", str(tmp_path / "app.py"))

    with log_app.app.test_client() as client:
        yield client

    # Cleanup any export files
    export_path = tmp_path / "logs.csv"
    if export_path.exists():
        try:
            export_path.unlink()
        except PermissionError:
            # Windows may still hold the file handle; ignore on teardown
            pass


def test_create_log_accepts_valid_payload(client):
    payload = {"level": "INFO", "message": "Started", "context": {"user": "alice"}}
    resp = client.post("/logs", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["level"] == "INFO"
    assert data["message"] == "Started"
    assert data["context"] == {"user": "alice"}
    assert "id" in data


def test_create_log_rejects_invalid_level(client):
    payload = {"level": "WARN", "message": "Bad level"}
    resp = client.post("/logs", json=payload)
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "invalid level"


def test_context_non_object_is_accepted(client):
    payload = {"level": "INFO", "message": "String ctx", "context": "just a string"}
    resp = client.post("/logs", json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["context"] == "just a string"


def test_list_logs_with_pagination_and_filter(client):
    # Create multiple logs
    for i in range(3):
        client.post("/logs", json={"level": "INFO", "message": f"msg{i}"})
    client.post("/logs", json={"level": "ERROR", "message": "boom"})

    # Default pagination
    resp = client.get("/logs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["page"] == 1
    assert data["per_page"] == 10
    assert len(data["items"]) == 4

    # Filter by level
    resp = client.get("/logs?level=ERROR")
    data = resp.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["level"] == "ERROR"

    # Pagination limit
    resp = client.get("/logs?per_page=2&page=1")
    data = resp.get_json()
    assert len(data["items"]) == 2


def test_delete_log(client):
    resp = client.post("/logs", json={"level": "INFO", "message": "to delete"})
    log_id = resp.get_json()["id"]
    del_resp = client.delete(f"/logs/{log_id}")
    assert del_resp.status_code == 204

    list_resp = client.get("/logs")
    ids = [item["id"] for item in list_resp.get_json()["items"]]
    assert log_id not in ids


def test_export_csv(client, tmp_path):
    client.post("/logs", json={"level": "INFO", "message": "export me", "context": {"user": "bob"}})
    resp = client.get("/export")
    assert resp.status_code == 200
    # Flask may return application/vnd.ms-excel for CSV downloads on Windows
    assert any(ct in resp.content_type for ct in ("text/csv", "octet-stream", "application/vnd.ms-excel"))

    content = resp.data.decode("utf-8")
    assert "id,level,message,context,created_at" in content.splitlines()[0]
    assert "export me" in content
    resp.close()

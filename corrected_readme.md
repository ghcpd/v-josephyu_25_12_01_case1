# Flask Log Management System (Corrected)

This Flask + SQLite service provides a minimal log management API. The database file is always `data.db` in the same directory as `app.py`.

## Requirements

- Python 3.8+ (tested with 3.13)
- Virtual environment name: `.venv`
- Dependencies: see `requirements.txt` (Flask + pytest for tests)

## Quick Start

### 1) Set up the environment

**Windows PowerShell**
```powershell
./setup.ps1    # use -Recreate to rebuild .venv
```

**Linux/macOS (bash)**
```bash
chmod +x setup.sh
./setup.sh      # pass --recreate to rebuild .venv
```

> After setup, activate if you want an interactive shell:
> - PowerShell: `./.venv/Scripts/Activate.ps1`
> - bash: `source .venv/bin/activate`

### 2) Initialize the database

```powershell
./.venv/Scripts/python.exe app.py --init-db
```

```bash
.venv/bin/python app.py --init-db
```

### 3) Run the server

```powershell
./.venv/Scripts/python.exe app.py
```

```bash
.venv/bin/python app.py
```

Server runs at `http://127.0.0.1:5000`.

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/logs` | POST | Create a log entry |
| `/logs` | GET | List logs (pagination + optional level filter) |
| `/logs/<id>` | DELETE | Delete a log by ID |
| `/export` | GET | Download all logs as `logs.csv` |

### Allowed levels

`DEBUG`, `INFO`, `WARNING`, `ERROR`  
> Note: `WARN` is **not** accepted by the server.

### POST /logs

- Content-Type: `application/json`
- Body fields:
  - `level` (string, required)
  - `message` (string, required)
  - `context` (JSON value, optional)

**Behavior**
- `context` is serialized with `json.dumps` if provided. The server does **not** enforce that it is an object; any JSON value is accepted, but using an object (dict) is recommended.
- Returns `201 Created` with the created log including `id` and `created_at` (UTC ISO8601).

**Example (PowerShell)**
```powershell
$body = @{ level = "INFO"; message = "Started"; context = @{ user = "alice" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body
```

**Example (curl)**
```bash
curl -X POST http://127.0.0.1:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level":"INFO","message":"Started","context":{"user":"alice"}}'
```

### GET /logs

Query parameters:
- `level` (optional): exact match (SQL `LIKE` with the provided string)
- `page` (default `1`)
- `per_page` (default `10`)

Response:
```json
{
  "items": [
    {"id": 1, "level": "INFO", "message": "Started", "context": {"user": "alice"}, "created_at": "..."}
  ],
  "page": 1,
  "per_page": 10
}
```

### DELETE /logs/<id>

- Returns `204 No Content` even if the ID did not exist.

### GET /export

- Returns a CSV download named `logs.csv` with columns: `id, level, message, context, created_at`.

## Testing

Run using the provided scripts or directly with pytest.

```powershell
./run_tests.ps1
```

```bash
./run_tests.sh
```

## Notes

- DB file **must** remain `data.db` in the app directory; the app always connects to that path.
- The server parses JSON with `force=True`; invalid JSON yields a 400 from Flask before handler logic.
- Deleting logs does not reclaim IDs; they auto-increment.

## Troubleshooting

- If you see `invalid level`, ensure the `level` is one of `DEBUG|INFO|WARNING|ERROR`.
- If `data.db` is missing, run with `--init-db`.
- PowerShell execution policy may block scripts; run in the same session with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` if needed.

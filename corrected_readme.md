# Flask Log Management System (Corrected)

This document provides working setup and API examples for a simple Flask-based log management system using SQLite.

- Database file: `data.db` in the application directory (same folder as `app.py`).
- Environment: use a virtual environment `.venv` (Windows PowerShell and Linux/macOS).

## Setup

1. Create and activate virtual environment, then install requirements:

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS (bash):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Initialize the database:

Windows PowerShell:
```powershell
python app.py --init-db
```

Linux/macOS (bash):
```bash
python3 app.py --init-db
```

3. Run the server:

Windows PowerShell:
```powershell
python app.py
```

Linux/macOS (bash):
```bash
python3 app.py
```

Notes:
- `app.py` does not read `FLASK_ENV`; debug mode in code determines behavior.
- Ensure you run commands from the application directory (`flask_logging_app`) so `data.db` is created there.

## API

### Create a log

Allowed levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`.

`context` may be any JSON value but it is recommended to send an object.

Windows PowerShell:
```powershell
# Windows PowerShell curl alias can be confusing; use Invoke-RestMethod
$body = @{ level = "INFO"; message = "Started"; context = @{ user = "alice" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body
```

Linux/macOS (bash):
```bash
curl -X POST http://127.0.0.1:5000/logs \
	-H "Content-Type: application/json" \
	-d '{"level": "INFO", "message": "Started", "context": {"user": "alice"}}'
```

### List logs (page + optional level filter)

- Exact match for `level` is recommended; avoid wildcard `%`.
- Defaults: `page=1`, `per_page=10`.

Windows PowerShell:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs?level=INFO&page=1&per_page=10"
```

Linux/macOS (bash):
```bash
curl "http://127.0.0.1:5000/logs?level=INFO&page=1&per_page=10"
```

### Delete a log by ID

Windows PowerShell:
```powershell
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:5000/logs/10"
```

Linux/macOS (bash):
```bash
curl -X DELETE "http://127.0.0.1:5000/logs/10"
```

### Export logs to CSV

Exports to `logs.csv` in the app directory. Re-running overwrites the file.

Windows PowerShell:
```powershell
Invoke-WebRequest -OutFile logs.csv -Uri "http://127.0.0.1:5000/export"
```

Linux/macOS (bash):
```bash
curl -o logs.csv "http://127.0.0.1:5000/export"
```

## Known Limitations (for testing)

- SQLite connections are not closed; concurrent write/export may cause `database is locked`.
- Level filter uses `LIKE`; wildcard patterns (e.g., `%`) will match broadly.
- `created_at` uses UTC without `Z` suffix.
- Export path is fixed and overwrites existing `logs.csv`.

## Minimal Test Steps (Windows)

```powershell
# Create INFO log
$body = @{ level = "INFO"; message = "Boot"; context = @{ host = "local" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body

# List
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs?page=1&per_page=5"

# Export
Invoke-WebRequest -OutFile logs.csv -Uri "http://127.0.0.1:5000/export"
```

## Minimal Test Steps (Linux/macOS)

```bash
# Create INFO log
curl -X POST http://127.0.0.1:5000/logs \
	-H "Content-Type: application/json" \
	-d '{"level":"INFO","message":"Boot","context":{"host":"local"}}'

# List
curl "http://127.0.0.1:5000/logs?page=1&per_page=5"

# Export
curl -o logs.csv "http://127.0.0.1:5000/export"
```

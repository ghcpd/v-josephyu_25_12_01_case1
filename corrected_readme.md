# Flask Log Management System (Corrected)

This README corrects earlier inconsistencies and adds test and setup steps.

## Quick Summary
- DB file is `data.db` located in the same folder as `app.py`.
- Allowed `level` values: `DEBUG`, `INFO`, `WARNING`, `ERROR`.
- `context` accepts any JSON value (object, string, number, array) and is stored as text; responses return the parsed JSON value.
- Exported CSV includes header: `id, level, message, context, created_at` and default filename `logs.csv`.

## Setup

Use a virtual environment named `.venv`.

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py --init-db
```

Linux/macOS (bash):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py --init-db
```

## Run server

Windows PowerShell:
```powershell
python app.py
```

Linux/macOS (bash):
```bash
python3 app.py
```

## API Examples

Create a log

Windows PowerShell:
```powershell
$body = @{
  level = "INFO"; 
  message = "Started"; 
  context = @{ user = "alice" }
} | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body
```

Linux/macOS (bash):
```bash
curl -X POST http://127.0.0.1:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level": "INFO", "message": "Started", "context": {"user": "alice"}}'
```

Notes: the `context` value in the request can be any JSON value; the response will include `context` as a parsed JSON value (object, string, number, array, or null).

List logs with pagination and filter

Windows PowerShell:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs?level=INFO&page=2&per_page=5"
```

Linux/macOS (bash):
```bash
curl "http://127.0.0.1:5000/logs?level=INFO&page=2&per_page=5"
```

Delete a log

Windows PowerShell:
```powershell
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:5000/logs/10"
```

Linux/macOS (bash):
```bash
curl -X DELETE "http://127.0.0.1:5000/logs/10"
```

Export CSV

Windows PowerShell:
```powershell
Invoke-WebRequest -OutFile logs.csv -Uri "http://127.0.0.1:5000/export"
```

Linux/macOS (bash):
```bash
curl -o logs.csv "http://127.0.0.1:5000/export"
```

## Testing (pytest)

Install and run tests (after activating `.venv`):

Windows PowerShell:
```powershell
pip install -r requirements.txt
pytest -q
```

Linux/macOS (bash):
```bash
pip install -r requirements.txt
pytest -q
```

## Notes and Clarifications
- Allowed levels: `DEBUG`, `INFO`, `WARNING`, `ERROR` (use `WARNING` not `WARN`).
- `context` may be any JSON value; if not provided it will be stored as `null`.
- CSV export has header and uses filename `logs.csv` via HTTP `Content-Disposition` header.
- The server reads/writes `data.db` in the same directory as `app.py`.
- When writing automation interacting with this API, ensure you pass `context` as valid JSON and `level` as one of the allowed values.

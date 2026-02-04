# Flask Log Management System (Corrected)

This is a corrected and verified tutorial for the Flask-based log management system.

Database file is `data.db` in the application directory (same folder as `app.py`).

## Key corrections
- Allowed levels are: **DEBUG**, **INFO**, **WARNING**, **ERROR** (note: **WARNING** not `WARN`).
- `level` is required and case-sensitive (must be uppercase).
- `context` can be any JSON-serializable value (object, array, string, number). It will be stored as text in the DB and returned as JSON when possible.
- The tutorial and examples were updated for Windows PowerShell to handle activation and JSON conversion depth.

## Features
- Create logs with `level`, `message`, and optional `context` (any JSON-serializable value)
- List logs with pagination
- Filter logs by `level` (exact uppercase match by default; code uses SQL LIKE so wildcards are possible)
- Delete logs by ID
- Export logs to CSV

## Quick Start
Use a virtual environment named `.venv`.

1. Create and activate `.venv`, then install requirements:

  Windows PowerShell (run as Administrator if Activate.ps1 is blocked):
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

  Linux/macOS (bash):
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  ```

2. Initialize database:

  Windows PowerShell:
  ```powershell
  python app.py --init-db
  ```

  Linux/macOS (bash):
  ```bash
  python3 app.py --init-db
  ```

3. Run server:

  Windows PowerShell:
  ```powershell
  python app.py
  ```

  Linux/macOS (bash):
  ```bash
  python3 app.py
  ```

4. API Examples

-- Create a log

  Windows PowerShell:
  ```powershell
  # use -Depth 10 for nested objects
  $body = @{ level = 'INFO'; message = 'Started'; context = @{ user = 'alice' } } | ConvertTo-Json -Depth 10
  Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:5000/logs' -ContentType 'application/json' -Body $body
  ```

  Linux/macOS (bash):
  ```bash
  curl -X POST http://127.0.0.1:5000/logs \
    -H 'Content-Type: application/json' \
    -d '{"level": "INFO", "message": "Started", "context": {"user": "alice"}}'
  ```

-- Create a log with a non-object context (also accepted):

  Linux/macOS (bash):
  ```bash
  curl -X POST http://127.0.0.1:5000/logs \
    -H 'Content-Type: application/json' \
    -d '{"level": "INFO", "message": "Ping", "context": "simple-string"}'
  ```

-- List logs (page + filter)

  Windows PowerShell:
  ```powershell
  Invoke-RestMethod -Uri 'http://127.0.0.1:5000/logs?level=INFO&page=1&per_page=5'
  ```

  Linux/macOS (bash):
  ```bash
  curl 'http://127.0.0.1:5000/logs?level=INFO&page=1&per_page=5'
  ```

-- Delete a log

  Windows PowerShell:
  ```powershell
  Invoke-RestMethod -Method Delete -Uri 'http://127.0.0.1:5000/logs/10'
  ```

  Linux/macOS (bash):
  ```bash
  curl -X DELETE 'http://127.0.0.1:5000/logs/10'
  ```

-- Export CSV

  Windows PowerShell:
  ```powershell
  Invoke-WebRequest -OutFile logs.csv -Uri 'http://127.0.0.1:5000/export'
  ```

  Linux/macOS (bash):
  ```bash
  curl -o logs.csv 'http://127.0.0.1:5000/export'
  ```

## Notes & Troubleshooting
- Allowed `level` values: `DEBUG`, `INFO`, `WARNING`, `ERROR` (uppercase only).
- `context` will be stored as text in the DB but returned as JSON when possible.
- The app exposes `--init-db` to create `data.db` in the application directory (same folder as `app.py`).
- If you run into SQLite file lock errors on Windows while manipulating `data.db`, ensure no other app has an open connection. The code may open connections without explicit closing — consider using `with sqlite3.connect(DB_PATH) as conn:` when modifying code.

## Development & Tests
- The project includes pytest-based tests in `test_files/` to verify endpoints.
- To run tests:

  Windows PowerShell:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  python -m pytest -q
  ```

  Linux/macOS (bash):
  ```bash
  source .venv/bin/activate
  python -m pytest -q
  ```

## Contact & Contributing
- If you notice mismatches between docs and code, open an issue or submit a PR.

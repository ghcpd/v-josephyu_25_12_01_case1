# Flask Log Management System

This tutorial shows how to run a simple Flask-based log management system using SQLite.

Database file is `data.db` in the application directory (same folder as `app.py`).

## Features

- Create logs with `level`, `message`, and optional `context`
- List logs with pagination
- Filter logs by `level`
- Delete logs by ID
- Export logs to CSV

## Quick Start

Use a virtual environment named `.venv`.

1. Create and activate `.venv`, then install requirements:
   
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
  $body = @{ level = "INFO"; message = "Started"; context = @{ user = "alice" } } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body
  ```

  Linux/macOS (bash):
  ```bash
  curl -X POST http://127.0.0.1:5000/logs \
    -H "Content-Type: application/json" \
    -d '{"level": "INFO", "message": "Started", "context": {"user": "alice"}}'
  ```

-- List logs (page + filter)
  
  Windows PowerShell:
  ```powershell
  Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs?level=INFO&page=2&per_page=5"
  ```

  Linux/macOS (bash):
  ```bash
  curl "http://127.0.0.1:5000/logs?level=INFO&page=2&per_page=5"
  ```

-- Delete a log
  
  Windows PowerShell:
  ```powershell
  Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:5000/logs/10"
  ```

  Linux/macOS (bash):
  ```bash
  curl -X DELETE "http://127.0.0.1:5000/logs/10"
  ```

-- Export CSV
  
  Windows PowerShell:
  ```powershell
  Invoke-WebRequest -OutFile logs.csv -Uri "http://127.0.0.1:5000/export"
  ```

  Linux/macOS (bash):
  ```bash
  curl -o logs.csv "http://127.0.0.1:5000/export"
  ```

## Notes

- Allowed levels: `DEBUG`, `INFO`, `WARN`, `ERROR`
- `context` must be a JSON object and will be stored as text.
- Pagination defaults: `page=1`, `per_page=10`.

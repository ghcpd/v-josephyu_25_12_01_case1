# Flask Log Management System

This tutorial shows how to run a simple Flask-based log management system using SQLite.

Database file is `data.db` in the application directory (same folder as `app.py`).

## Features

- Create logs with `level`, `message`, and optional `context`
- List logs with pagination
- Filter logs by `level` (uses SQL LIKE pattern matching)
- Delete logs by ID
- Export logs to CSV

## Quick Start

Use a virtual environment named `.venv`.

### 1. Create and activate `.venv`, then install requirements

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Note for Windows users:** If you get an error about execution policy, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS (bash):**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the application

The database will be automatically created on first run. You can optionally initialize it explicitly with `--init-db`, but note that this flag also starts the server.

**Windows PowerShell:**

```powershell
python app.py
```

**Linux/macOS (bash):**

```bash
python3 app.py
```

The server will start on `http://127.0.0.1:5000`.

**Note:** If you want to start fresh, delete `data.db` before running the application.

## API Documentation

### Create a Log

**Endpoint:** `POST /logs`

**Request Body:**
```json
{
  "level": "INFO",
  "message": "Your log message",
  "context": {"key": "value"}
}
```

**Fields:**
- `level` (required): Must be one of: `DEBUG`, `INFO`, `WARNING`, `ERROR`
- `message` (required): String message
- `context` (optional): JSON object or null. Will be stored as text.

**Response:** `201 Created`
```json
{
  "id": 1,
  "level": "INFO",
  "message": "Your log message",
  "context": {"key": "value"},
  "created_at": "2025-12-01T05:39:22.018617"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "error": "invalid level"
}
```

**Examples:**

Windows PowerShell:
```powershell
$body = @{ level = "INFO"; message = "Application started"; context = @{ user = "alice"; session = "12345" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body
```

Linux/macOS (bash):
```bash
curl -X POST http://127.0.0.1:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level": "INFO", "message": "Application started", "context": {"user": "alice", "session": "12345"}}'
```

### List Logs

**Endpoint:** `GET /logs`

**Query Parameters:**
- `level` (optional): Filter logs by level using SQL LIKE pattern matching
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "level": "INFO",
      "message": "Application started",
      "context": {"user": "alice"},
      "created_at": "2025-12-01T05:39:22.018617"
    }
  ],
  "page": 1,
  "per_page": 10
}
```

**Examples:**

Windows PowerShell:
```powershell
# Get all logs (first page)
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs"

# Filter by level with pagination
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs?level=INFO&page=1&per_page=5"

# Get second page
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs?page=2&per_page=10"
```

Linux/macOS (bash):
```bash
# Get all logs (first page)
curl "http://127.0.0.1:5000/logs"

# Filter by level with pagination
curl "http://127.0.0.1:5000/logs?level=INFO&page=1&per_page=5"

# Get second page
curl "http://127.0.0.1:5000/logs?page=2&per_page=10"
```

### Delete a Log

**Endpoint:** `DELETE /logs/<id>`

**Response:** `204 No Content` (empty body)

**Examples:**

Windows PowerShell:
```powershell
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:5000/logs/1"
```

Linux/macOS (bash):
```bash
curl -X DELETE "http://127.0.0.1:5000/logs/1"
```

### Export Logs to CSV

**Endpoint:** `GET /export`

**Response:** CSV file download

**Note:** The server also creates a `logs.csv` file in the application directory.

**Examples:**

Windows PowerShell:
```powershell
Invoke-WebRequest -OutFile logs.csv -Uri "http://127.0.0.1:5000/export"
```

Linux/macOS (bash):
```bash
curl -o logs.csv "http://127.0.0.1:5000/export"
```

## Database Schema

The application uses SQLite with a single table:

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    context TEXT,
    created_at TEXT NOT NULL
);
```

**Columns:**
- `id`: Auto-incrementing integer primary key
- `level`: Text field storing one of: DEBUG, INFO, WARNING, ERROR
- `message`: Text field for the log message
- `context`: Text field storing JSON-serialized context (can be NULL)
- `created_at`: Text field storing ISO 8601 timestamp

## Complete Example Workflow

Here's a complete example to test all endpoints:

**Windows PowerShell:**

```powershell
# 1. Create several logs
$body1 = @{ level = "INFO"; message = "Server started"; context = @{ version = "1.0" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body1

$body2 = @{ level = "WARNING"; message = "High memory usage"; context = @{ memory = "85%" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body2

$body3 = @{ level = "ERROR"; message = "Connection failed"; context = @{ host = "db.example.com" } } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" -ContentType "application/json" -Body $body3

# 2. List all logs
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs"

# 3. Filter by WARNING level
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs?level=WARNING"

# 4. Export to CSV
Invoke-WebRequest -OutFile logs.csv -Uri "http://127.0.0.1:5000/export"

# 5. View CSV content
Get-Content logs.csv

# 6. Delete a log (replace 1 with actual ID from step 2)
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:5000/logs/1"

# 7. Verify deletion
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs"
```

**Linux/macOS (bash):**

```bash
# 1. Create several logs
curl -X POST http://127.0.0.1:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level": "INFO", "message": "Server started", "context": {"version": "1.0"}}'

curl -X POST http://127.0.0.1:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level": "WARNING", "message": "High memory usage", "context": {"memory": "85%"}}'

curl -X POST http://127.0.0.1:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level": "ERROR", "message": "Connection failed", "context": {"host": "db.example.com"}}'

# 2. List all logs
curl "http://127.0.0.1:5000/logs"

# 3. Filter by WARNING level
curl "http://127.0.0.1:5000/logs?level=WARNING"

# 4. Export to CSV
curl -o logs.csv "http://127.0.0.1:5000/export"

# 5. View CSV content
cat logs.csv

# 6. Delete a log (replace 1 with actual ID from step 2)
curl -X DELETE "http://127.0.0.1:5000/logs/1"

# 7. Verify deletion
curl "http://127.0.0.1:5000/logs"
```

## Troubleshooting

### Port Already in Use

If you see an error that port 5000 is already in use:

**Windows:**
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Linux/macOS:**
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9
```

### Execution Policy Error (Windows)

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Database Locked Error

If you get a "database is locked" error:
1. Stop all running instances of the application
2. Delete `data.db` and restart

### Starting Fresh

To completely reset the application:

**Windows PowerShell:**
```powershell
# Stop the server (Ctrl+C in the terminal where it's running)
# Then delete the database
Remove-Item data.db -ErrorAction SilentlyContinue
Remove-Item logs.csv -ErrorAction SilentlyContinue
```

**Linux/macOS:**
```bash
# Stop the server (Ctrl+C in the terminal where it's running)
# Then delete the database
rm -f data.db logs.csv
```

## Notes

- **Allowed levels:** `DEBUG`, `INFO`, `WARNING`, `ERROR` (case-sensitive)
- **Context field:** Optional JSON object. Can be null or omitted. Stored as text in database.
- **Pagination defaults:** `page=1`, `per_page=10`
- **Level filtering:** Uses SQL LIKE pattern matching, so partial matches may occur
- **Timestamps:** Stored in ISO 8601 format (UTC)
- **Database location:** Always `data.db` in the same directory as `app.py`
- **CSV export:** Creates both a download and a local `logs.csv` file in the application directory

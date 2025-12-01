# Flask Log Management System - Corrected Documentation

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

### 1. Create and activate `.venv`, then install requirements:

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/macOS (bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize database:

The following command creates the SQLite database with the required schema. The database file will be created as `data.db` in the application directory. It is safe to run this command multiple times.

**Windows PowerShell:**
```powershell
python app.py --init-db
```

**Linux/macOS (bash):**
```bash
python3 app.py --init-db
```

Expected output:
```
Database initialized successfully at: <app-directory>\data.db
```

After database initialization, the command will exit. Do not start the server with this flag.

### 3. Run server:

**Windows PowerShell:**
```powershell
python app.py
```

**Linux/macOS (bash):**
```bash
python3 app.py
```

Server will start on `http://127.0.0.1:5000` with debug mode enabled.

## API Endpoints

### Create a Log (POST /logs)

Create a new log entry with a required level and message, and optional context.

**Request Parameters:**
- `level` (required): One of `DEBUG`, `INFO`, `WARNING`, or `ERROR`
- `message` (required): String message for the log entry
- `context` (optional): JSON object containing additional context information

**Response:** Returns the created log entry with ID and created timestamp (HTTP 201)

**Windows PowerShell:**
```powershell
$body = @{
    level = "INFO"
    message = "Started"
    context = @{ user = "alice" }
} | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/logs" `
    -ContentType "application/json" -Body $body
```

**Linux/macOS (bash):**
```bash
curl -X POST http://127.0.0.1:5000/logs \
  -H "Content-Type: application/json" \
  -d '{"level": "INFO", "message": "Started", "context": {"user": "alice"}}'
```

**Example Response:**
```json
{
  "id": 1,
  "level": "INFO",
  "message": "Started",
  "context": {"user": "alice"},
  "created_at": "2025-11-30T10:30:45.123456"
}
```

### List Logs (GET /logs)

Retrieve logs with optional filtering and pagination.

**Query Parameters:**
- `level` (optional): Filter logs by level (exact match)
- `page` (optional): Page number, defaults to 1
- `per_page` (optional): Items per page, defaults to 10

**Response:** Returns paginated log entries (HTTP 200)

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:5000/logs?level=INFO&page=1&per_page=5"
```

**Linux/macOS (bash):**
```bash
curl "http://127.0.0.1:5000/logs?level=INFO&page=1&per_page=5"
```

**Example Response:**
```json
{
  "items": [
    {
      "id": 2,
      "level": "INFO",
      "message": "Started",
      "context": null,
      "created_at": "2025-11-30T10:30:46.654321"
    }
  ],
  "page": 1,
  "per_page": 5
}
```

### Delete a Log (DELETE /logs/<id>)

Delete a specific log entry by ID.

**Path Parameters:**
- `id` (required): The log ID to delete

**Response:** HTTP 204 (No Content) on success

**Windows PowerShell:**
```powershell
Invoke-RestMethod -Method Delete -Uri "http://127.0.0.1:5000/logs/1"
```

**Linux/macOS (bash):**
```bash
curl -X DELETE "http://127.0.0.1:5000/logs/1"
```

### Export Logs to CSV (GET /export)

Export all logs as a CSV file. This endpoint retrieves all logs from the database and returns them in CSV format with the following columns: `id`, `level`, `message`, `context`, `created_at`.

The CSV file will be downloaded with the filename `logs.csv`.

**Response:** CSV file (HTTP 200) with `Content-Type: text/csv`

**Windows PowerShell:**
```powershell
Invoke-WebRequest -OutFile logs.csv -Uri "http://127.0.0.1:5000/export"
```

**Linux/macOS (bash):**
```bash
curl -o logs.csv "http://127.0.0.1:5000/export"
```

**Example CSV Output:**
```
id,level,message,context,created_at
1,INFO,Application started,"{""user"": ""alice""}",2025-11-30T10:30:45.123456
2,ERROR,Database connection failed,null,2025-11-30T10:30:46.654321
```

## Important Notes

### Allowed Log Levels
The system supports exactly four log levels:
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages (note: use `WARNING`, not `WARN`)
- `ERROR` - Error messages

**⚠️ Important:** The correct level name is `WARNING`, not `WARN`. Using `WARN` will result in a 400 Bad Request error.

### Context Parameter
- `context` must be a valid JSON object (e.g., `{"user": "alice", "request_id": "123"}`)
- If provided, `context` will be stored as JSON text in the database
- When retrieved, `context` is returned as a JSON object, not a string
- `context` is optional; you can omit it or set it to `null`

### Pagination
- Default page: `1` (first page)
- Default per_page: `10` items per page
- Pages are 1-indexed (page 1 is the first page)
- Logs are returned in descending order by ID (newest first)

### Level Filtering
- The `level` parameter is case-sensitive (must match exactly: `DEBUG`, `INFO`, `WARNING`, or `ERROR`)
- If you specify a level that doesn't exist in the database, an empty list is returned (no error)

## Troubleshooting

### Database file not found
**Issue:** Error like "database is locked" or "database does not exist"
**Solution:** Run `python app.py --init-db` to create the database

### "invalid level" error
**Issue:** POST to `/logs` returns `{"error": "invalid level"}`
**Solution:** Ensure you're using one of the four allowed levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`. Note: `WARN` is not valid (use `WARNING` instead)

### "message must be string" error
**Issue:** POST to `/logs` returns `{"error": "message must be string"}`
**Solution:** Ensure the `message` parameter is a string, not a number, boolean, or object

### Port already in use
**Issue:** "Address already in use" when starting the server
**Solution:** Either stop the existing server or specify a different port

### PowerShell execution policy
**Issue:** Cannot run `.venv\Scripts\Activate.ps1`
**Solution:** Set execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Database Schema

The application uses SQLite with the following table structure:

```sql
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    context TEXT,
    created_at TEXT NOT NULL
);
```

- `id`: Unique identifier (auto-incrementing)
- `level`: One of DEBUG, INFO, WARNING, ERROR
- `message`: The log message (string)
- `context`: Optional JSON context stored as text
- `created_at`: ISO 8601 UTC timestamp

## Environment

- **Python:** 3.13.x recommended (tested with 3.13.9)
- **Framework:** Flask 3.0.0
- **Database:** SQLite3 (built-in)
- **Required Packages:** See requirements.txt

## Additional Information

All timestamps are in UTC (ISO 8601 format) using `datetime.now(timezone.utc)`.

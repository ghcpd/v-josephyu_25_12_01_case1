import os
import json
import csv
import argparse
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import sqlite3

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'data.db')

def get_conn():
    return sqlite3.connect(DB_PATH)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    context TEXT,
    created_at TEXT NOT NULL
);
"""

ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA_SQL)
    conn.commit()

@app.route('/logs', methods=['POST'])
def create_log():
    data = request.get_json(force=True)
    level = data.get('level')
    message = data.get('message')
    context = data.get('context')

    if level not in ALLOWED_LEVELS:
        return jsonify({"error": "invalid level"}), 400
    if not isinstance(message, str):
        return jsonify({"error": "message must be string"}), 400
    if context is None:
        context_str = None
    else:
        context_str = json.dumps(context)

    created_at = datetime.utcnow().isoformat()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO logs(level, message, context, created_at) VALUES(?,?,?,?)',
        (level, message, context_str, created_at)
    )
    conn.commit()
    log_id = cur.lastrowid
    return jsonify({"id": log_id, "level": level, "message": message, "context": context, "created_at": created_at}), 201

@app.route('/logs', methods=['GET'])
def list_logs():
    level = request.args.get('level')
    page = int(request.args.get('page', '1'))
    per_page = int(request.args.get('per_page', '10'))
    offset = (page - 1) * per_page

    conn = get_conn()
    cur = conn.cursor()
    if level:
        cur.execute('SELECT id, level, message, context, created_at FROM logs WHERE level LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?', (level, per_page, offset))
    else:
        cur.execute('SELECT id, level, message, context, created_at FROM logs ORDER BY id DESC LIMIT ? OFFSET ?', (per_page, offset))
    rows = cur.fetchall()
    result = []
    for r in rows:
        ctx = r[3]
        try:
            ctx_obj = json.loads(ctx) if ctx else None
        except Exception:
            ctx_obj = ctx
        result.append({
            "id": r[0],
            "level": r[1],
            "message": r[2],
            "context": ctx_obj,
            "created_at": r[4]
        })
    return jsonify({"items": result, "page": page, "per_page": per_page})

@app.route('/logs/<int:log_id>', methods=['DELETE'])
def delete_log(log_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM logs WHERE id=?', (log_id,))
    conn.commit()

    return ('', 204)

@app.route('/export', methods=['GET'])
def export_csv():
    export_path = os.path.join(os.path.dirname(__file__), 'logs.csv')
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT id, level, message, context, created_at FROM logs ORDER BY id DESC')
    rows = cur.fetchall()
    with open(export_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'level', 'message', 'context', 'created_at'])
        writer.writerows(rows)
    return send_file(export_path, as_attachment=True, download_name='logs.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--init-db', action='store_true')
    args = parser.parse_args()
    if args.init_db:
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)

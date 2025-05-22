"""Simple cache store for agent memory."""

import os
import sqlite3
import threading
import json
from datetime import datetime

# Initialize SQLite database for caching
_DB_PATH = os.getenv('AGENT_MEMORY_DB', os.path.join(os.getcwd(), 'agent_memory.db'))
_conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
_conn.execute(
    'CREATE TABLE IF NOT EXISTS memory ('
    'key TEXT PRIMARY KEY, '
    'result TEXT, '
    'timestamp TEXT'
    ')'
)
_conn.commit()
_lock = threading.Lock()

def get_cache(key: str):
    """Retrieve cached result by key (returns Python object or None)."""
    with _lock:
        cur = _conn.cursor()
        cur.execute('SELECT result FROM memory WHERE key = ?', (key,))
        row = cur.fetchone()
    if row:
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return row[0]
    return None

def set_cache(key: str, result):
    """Store result in cache with timestamp."""
    text = json.dumps(result)
    ts = datetime.utcnow().isoformat()
    with _lock:
        cur = _conn.cursor()
        cur.execute(
            'INSERT OR REPLACE INTO memory (key, result, timestamp) VALUES (?, ?, ?)',
            (key, text, ts)
        )
        _conn.commit()
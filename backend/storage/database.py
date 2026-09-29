import sqlite3
import os
import json
import time
from typing import List, Dict, Any, Optional

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "snapassist.db")

def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Initialize database and create schema if not exists."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Documents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        file_path TEXT NOT NULL,
        page_count INTEGER DEFAULT 1,
        chunk_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        summary_json TEXT,
        created_at REAL NOT NULL,
        updated_at REAL NOT NULL
    )
    """)

    # Chunks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id TEXT PRIMARY KEY,
        doc_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        page_number INTEGER NOT NULL,
        content TEXT NOT NULL,
        token_count INTEGER DEFAULT 0,
        embedding_blob BLOB,
        created_at REAL NOT NULL,
        FOREIGN KEY (doc_id) REFERENCES documents (id) ON DELETE CASCADE
    )
    """)

    # Chat history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id TEXT PRIMARY KEY,
        session_id TEXT DEFAULT 'default',
        doc_id TEXT,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        citations_json TEXT,
        latency_ms REAL DEFAULT 0,
        tokens_used INTEGER DEFAULT 0,
        created_at REAL NOT NULL
    )
    """)

    # Privacy & Security Audit Log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        target TEXT,
        is_local INTEGER DEFAULT 1,
        bytes_outbound INTEGER DEFAULT 0,
        external_api_calls INTEGER DEFAULT 0,
        timestamp REAL NOT NULL,
        details TEXT
    )
    """)

    # Performance Telemetry
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS performance_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        operation TEXT NOT NULL,
        model_name TEXT NOT NULL,
        backend_name TEXT NOT NULL,
        execution_provider TEXT NOT NULL,
        latency_ms REAL NOT NULL,
        throughput_tokens_sec REAL DEFAULT 0,
        memory_mb REAL DEFAULT 0,
        timestamp REAL NOT NULL
    )
    """)

    # System configuration / status
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at REAL NOT NULL
    )
    """)

    conn.commit()
    return conn

# Global connection accessor
_conn: Optional[sqlite3.Connection] = None

def get_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = init_db(db_path)
    return _conn

def record_audit(action: str, target: str = "", details: str = "", bytes_outbound: int = 0, external_api_calls: int = 0):
    """Log an operation to the privacy audit table."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_log (action, target, is_local, bytes_outbound, external_api_calls, timestamp, details)
        VALUES (?, ?, 1, ?, ?, ?, ?)
    """, (action, target, bytes_outbound, external_api_calls, time.time(), details))
    conn.commit()

def record_performance(operation: str, model_name: str, backend_name: str, execution_provider: str, latency_ms: float, throughput: float = 0.0, memory_mb: float = 0.0):
    """Log a performance measurement."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO performance_metrics (operation, model_name, backend_name, execution_provider, latency_ms, throughput_tokens_sec, memory_mb, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (operation, model_name, backend_name, execution_provider, latency_ms, throughput, memory_mb, time.time()))
    conn.commit()

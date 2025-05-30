#!/usr/bin/env python3
"""
Fix the database migration issue by ensuring the base request_logs table is created.
"""
import sqlite3
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mockloop_mcp.database_migration import DatabaseMigrator

def fix_database(db_path):
    """Fix the database by ensuring all tables are created properly."""
    print(f"Fixing database at: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    print(f"Existing tables: {existing_tables}")
    
    # If request_logs table doesn't exist, create it manually
    if 'request_logs' not in existing_tables:
        print("Creating request_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                type TEXT,
                method TEXT,
                path TEXT,
                status_code INTEGER,
                process_time_ms INTEGER,
                client_host TEXT,
                client_port TEXT,
                headers TEXT,
                query_params TEXT,
                request_body TEXT,
                response_body TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT,
                test_scenario TEXT,
                correlation_id TEXT,
                user_agent TEXT,
                response_size INTEGER,
                is_admin BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
        print("✅ request_logs table created")
    
    # Check final state
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    final_tables = {row[0] for row in cursor.fetchall()}
    print(f"Final tables: {final_tables}")
    
    conn.close()
    return True

if __name__ == "__main__":
    # Fix the test database
    db_path = Path("generated_mocks/final_integration_test_server/db/request_logs.db")
    if db_path.exists():
        fix_database(db_path)
    else:
        print("Database does not exist")
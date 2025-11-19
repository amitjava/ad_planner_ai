"""SQLite Memory Manager"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path


class SQLiteMemory:
    """Manages SQLite database operations"""

    def __init__(self, db_path: str = "ad_planner.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database with schema"""
        schema_path = Path(__file__).parent.parent.parent / "db" / "init.sql"

        with sqlite3.connect(self.db_path) as conn:
            if schema_path.exists():
                with open(schema_path, 'r') as f:
                    conn.executescript(f.read())
            else:
                # Fallback schema if file not found
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        profile_json TEXT,
                        plan_json TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    );
                    CREATE TABLE IF NOT EXISTS feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        plan_type TEXT,
                        rating INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event TEXT,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

    def create_session(self, session_id: str) -> int:
        """Create new user session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO users (session_id) VALUES (?)",
                (session_id,)
            )
            return cursor.lastrowid

    def get_user_by_session(self, session_id: str) -> Optional[int]:
        """Get user ID by session ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM users WHERE session_id = ?",
                (session_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def save_plan(self, user_id: int, profile: Dict[Any, Any], plan: Dict[Any, Any]) -> int:
        """Save a generated plan"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO plans (user_id, profile_json, plan_json) VALUES (?, ?, ?)",
                (user_id, json.dumps(profile), json.dumps(plan))
            )
            return cursor.lastrowid

    def get_plan(self, plan_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a plan by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT profile_json, plan_json, created_at FROM plans WHERE id = ?",
                (plan_id,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    "profile": json.loads(result[0]),
                    "plan": json.loads(result[1]),
                    "created_at": result[2]
                }
            return None

    def save_feedback(self, user_id: int, plan_type: str, rating: int):
        """Save user feedback"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO feedback (user_id, plan_type, rating) VALUES (?, ?, ?)",
                (user_id, plan_type, rating)
            )

    def log_event(self, event: str, details: Dict[Any, Any]):
        """Log an event"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO logs (event, details) VALUES (?, ?)",
                (event, json.dumps(details))
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM plans")
            total_plans = cursor.fetchone()[0]

            cursor = conn.execute("SELECT AVG(rating) FROM feedback")
            avg_rating = cursor.fetchone()[0] or 0

            cursor = conn.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]

            return {
                "total_plans": total_plans,
                "total_users": total_users,
                "avg_rating": round(avg_rating, 2)
            }

    def get_recent_plans(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent plans"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id, profile_json, plan_json, created_at FROM plans ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            results = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "profile": json.loads(row[1]),
                    "plan": json.loads(row[2]),
                    "created_at": row[3]
                }
                for row in results
            ]

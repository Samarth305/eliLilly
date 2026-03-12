import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class CacheService:
    def __init__(self, db_path: str = "repository_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repository_cache (
                    repo_url TEXT PRIMARY KEY,
                    latest_commit_sha TEXT,
                    analysis_data TEXT,
                    last_updated TIMESTAMP
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_repo_url ON repository_cache(repo_url);")
            conn.commit()

    def get_cached_analysis(self, repo_url: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis if it exists."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT latest_commit_sha, analysis_data, last_updated FROM repository_cache WHERE repo_url = ?",
                    (repo_url,)
                )
                row = cursor.fetchone()
                
                if row:
                    sha, data_json, updated = row
                    return {
                        "repo_url": repo_url,
                        "latest_commit_sha": sha,
                        "analysis_data": json.loads(data_json),
                        "last_updated": updated
                    }
        except Exception as e:
            print(f"Cache retrieval error: {e}")
        return None

    def save_analysis(self, repo_url: str, latest_commit_sha: str, analysis_data: Dict[str, Any]):
        """Save analysis results to cache with size limit control."""
        try:
            with self._get_connection() as conn:
                # 1. Insert or Replace
                conn.execute(
                    """
                    INSERT OR REPLACE INTO repository_cache (repo_url, latest_commit_sha, analysis_data, last_updated)
                    VALUES (?, ?, ?, ?)
                    """,
                    (repo_url, latest_commit_sha, json.dumps(analysis_data, default=str), datetime.now().isoformat())
                )
                
                # 2. Enforce size limit (100 repositories)
                conn.execute(
                    """
                    DELETE FROM repository_cache
                    WHERE repo_url NOT IN (
                        SELECT repo_url
                        FROM repository_cache
                        ORDER BY last_updated DESC
                        LIMIT 100
                    )
                    """
                )
                conn.commit()
        except Exception as e:
            print(f"Cache save error: {e}")

    def invalidate_cache(self, repo_url: str):
        """Manually invalidate cache for a specific repo."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM repository_cache WHERE repo_url = ?", (repo_url,))
                conn.commit()
        except Exception as e:
            print(f"Cache invalidation error: {e}")

    def clear_all_cache(self):
        """Invalidate the entire cache."""
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM repository_cache")
                conn.commit()
        except Exception as e:
            print(f"Clear all cache error: {e}")

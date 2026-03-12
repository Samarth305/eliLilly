import sqlite3
import json
import os

def inspect_cache():
    db_path = "repository_cache.db"
    if not os.path.exists(db_path):
        # Check if the test DB exists instead, just in case
        if os.path.exists("test_repository_cache.db"):
            db_path = "test_repository_cache.db"
        else:
            print(f"Database file not found. Try analyzing a repository in the UI first!")
            return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all entries
        cursor.execute("SELECT repo_url, latest_commit_sha, last_updated FROM repository_cache")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"The cache in '{db_path}' is currently empty.")
            return

        print(f"\n{'Repository URL':<50} | {'Latest SHA':<12} | {'Last Updated'}")
        print("-" * 100)
        for url, sha, updated in rows:
            # Handle potentially None SHA
            display_sha = str(sha)[:10] if sha else "N/A"
            print(f"{url[:50]:<50} | {display_sha:<12} | {updated}")
        print(f"\nTotal cached repositories: {len(rows)}")
            
    except Exception as e:
        print(f"Error reading database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_cache()

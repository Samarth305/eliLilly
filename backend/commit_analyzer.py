import re
from typing import Dict, Any

class CommitAnalyzer:
    @staticmethod
    def classify_commit(message: str) -> str:
        """Classify a commit into types based on keywords."""
        message = message.lower()
        
        if re.search(r'\b(add|implement|introduce|feature|feat)\b', message):
            return "feature"
        elif re.search(r'\b(fix|bug|resolve|patch)\b', message):
            return "bugfix"
        elif re.search(r'\b(refactor|cleanup)\b', message):
            return "refactor"
        elif re.search(r'\b(optimize|perf|performance)\b', message):
            return "performance"
        elif re.search(r'\b(upgrade|update|bump|dep|dependencies)\b', message):
            return "dependency"
        elif re.search(r'\b(test|tests)\b', message):
            return "testing"
        elif re.search(r'\b(docs|doc)\b', message):
            return "documentation"
        else:
            return "other"
            
    @staticmethod
    def extract_summary(commit_detail: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a simplified summary of a commit's details."""
        commit = commit_detail.get('commit', {})
        stats = commit_detail.get('stats', {})
        files = commit_detail.get('files', [])
        
        message = commit.get('message', '')
        author = commit.get('author', {}).get('name', 'Unknown')
        date = commit.get('author', {}).get('date', '')
        
        files_changed = [f.get('filename') for f in files] if files else []
        
        # Determine if it's a merge commit (usually more than one parent)
        parents = commit_detail.get('parents', [])
        is_merge = len(parents) > 1
        
        return {
            "sha": commit_detail.get("sha"),
            "message": message,
            "type": CommitAnalyzer.classify_commit(message),
            "author": author,
            "date": date,
            "files": files,
            "files_changed": files_changed,
            "additions": stats.get('additions', 0),
            "deletions": stats.get('deletions', 0),
            "is_merge": is_merge
        }

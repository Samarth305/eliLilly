import os
import re
from datetime import datetime

class RequestUtils:
    @staticmethod
    def get_env_var(var_name: str, default: str = "") -> str:
        return os.getenv(var_name, default)

def parse_github_url(url: str):
    """
    Parses a GitHub URL and returns the owner and repo name.
    """
    url = url.strip()
    # Remove trailing slash
    if url.endswith("/"):
        url = url[:-1]
    
    # Extract owner and repo from url (e.g., https://github.com/owner/repo)
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid GitHub URL provided.")
    
    owner = match.group(1)
    repo = match.group(2)
    
    # Remove any .git extension
    if repo.endswith(".git"):
        repo = repo[:-4]
        
    return owner, repo

def parse_date(date_str: str) -> datetime:
    """Parse ISO standard github date strings into datetime."""
    # GitHub returns strings like 2021-01-01T00:00:00Z
    if not date_str:
        return datetime.utcnow()
    date_str = date_str.replace("Z", "+00:00")
    try:
        from dateutil import parser
        return parser.isoparse(date_str)
    except ImportError:
        # Fallback if dateutil is not available
        return datetime.fromisoformat(date_str)

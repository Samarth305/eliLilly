from typing import List, Dict, Any
from utils import parse_date

class MilestoneDetector:
    @staticmethod
    def detect_repository_creation(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not commits:
            return {}
        
        # Commits should be sorted chronologically to find the true first
        valid_commits = [c for c in commits if c.get("date")]
        if not valid_commits:
            return {}
            
        valid_commits.sort(key=lambda x: parse_date(x["date"]))
        first = valid_commits[0]
        
        return {
            "date": first["date"],
            "event_description": f"Repository created by {first.get('author')}."
        }
        
    @staticmethod
    def detect_component_introductions(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        seen_components = set()
        
        # Parse commits chronologically
        valid_commits = [c for c in commits if c.get("date")]
        valid_commits.sort(key=lambda x: parse_date(x["date"]))
        
        for commit in valid_commits:
            files = commit.get("files_changed", [])
            for f in files:
                if f.startswith("tests/") and "testing" not in seen_components:
                    seen_components.add("testing")
                    milestones.append({
                        "date": commit["date"],
                        "event_description": "Testing framework/tests directory introduced."
                    })
                if f in ["Dockerfile", "docker-compose.yml"] and "docker" not in seen_components:
                    seen_components.add("docker")
                    milestones.append({
                        "date": commit["date"],
                        "event_description": "Docker infrastructure added."
                    })
                if f.startswith(".github/workflows/") and "ci" not in seen_components:
                    seen_components.add("ci")
                    milestones.append({
                        "date": commit["date"],
                        "event_description": "GitHub Actions CI pipeline introduced."
                    })
        return milestones

    @staticmethod
    def generate_milestones(commits: List[Dict[str, Any]], releases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        
        creation = MilestoneDetector.detect_repository_creation(commits)
        if creation:
            milestones.append(creation)
            
        milestones.extend(MilestoneDetector.detect_component_introductions(commits))
        
        # Add releases as milestones
        for release in releases:
            date = release.get("published_at") or release.get("created_at")
            if date:
                milestones.append({
                    "date": date,
                    "event_description": f"Release: {release.get('name') or release.get('tag_name')}"
                })
                
        # Sort milestones by date
        milestones.sort(key=lambda m: parse_date(m["date"]))
        return milestones

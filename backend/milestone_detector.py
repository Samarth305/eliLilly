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
        import re
        milestones = []
        seen_components = set()
        
        # Parse commits chronologically
        valid_commits = sorted([c for c in commits if c.get("date")], key=lambda x: parse_date(x["date"]))
        
        for commit in valid_commits:
            files = commit.get("files_changed", [])
            for f in files:
                if "testing" not in seen_components and (f.startswith("tests/") or re.search(r'(^|/)test_|\.test\.|\.spec\.', f)):
                    seen_components.add("testing")
                    milestones.append({
                        "date": commit["date"],
                        "type": "testing_framework_introduction",
                        "event_description": "Testing framework or comprehensive test suite introduced."
                    })
                
                # Covers Docker, Github Actions, Jenkins, Makefiles
                if "infra" not in seen_components and (f in ["Dockerfile", "docker-compose.yml", "Jenkinsfile", "Makefile"] or f.startswith(".github/workflows/")):
                    seen_components.add("infra")
                    milestones.append({
                        "date": commit["date"],
                        "type": "infrastructure_changes",
                        "event_description": "Project infrastructure (CI/CD/Docker Automation) introduced."
                    })
        return milestones

    @staticmethod
    def detect_module_introductions(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        from collections import defaultdict
        milestones = []
        seen_dirs = set()
        dir_file_counts = defaultdict(int)
        
        valid_commits = sorted([c for c in commits if c.get("date")], key=lambda x: parse_date(x["date"]))
        
        for commit in valid_commits:
            files = commit.get("files", [])
            
            for f in files:
                status = f.get("status")
                if not status:
                    continue
                filename = f.get("filename", "")
                if status == "added" and "/" in filename:
                    top_dir = filename.split("/")[0]
                    if top_dir not in seen_dirs:
                        dir_file_counts[top_dir] += 1
                        if dir_file_counts[top_dir] >= 5:
                            seen_dirs.add(top_dir)
                            milestones.append({
                                "type": "module_introduction",
                                "module": top_dir,
                                "date": commit["date"],
                                "event_description": f"New major module established: {top_dir} (reached 5 cumulative files)."
                            })
        return milestones

    @staticmethod
    def detect_contributor_growth(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        monthly_contributors = {}
        
        for c in commits:
            date_str = c.get("date")
            author = c.get("author")
            if date_str and author:
                month_str = date_str[:7]
                if month_str not in monthly_contributors:
                    monthly_contributors[month_str] = set()
                monthly_contributors[month_str].add(author)
                
        sorted_months = sorted(monthly_contributors.keys())
        for i in range(1, len(sorted_months)):
            curr_month = sorted_months[i]
            curr_count = len(monthly_contributors[curr_month])
            
            # Comparison using a moving average of the previous 3 months
            lookback_range = sorted_months[max(0, i-3):i]
            if not lookback_range:
                continue
                
            avg_prev_count = sum(len(monthly_contributors[m]) for m in lookback_range) / len(lookback_range)
            
            # Fire milestone if current count is at least double the moving average
            if avg_prev_count > 0 and curr_count >= avg_prev_count * 2 and curr_count > 2:
                milestones.append({
                    "type": "contributor_growth",
                    "date": curr_month + "-01T00:00:00Z",
                    "event_description": f"Active contributors surged to {curr_count} (double the 3-month average of {avg_prev_count:.1f})."
                })
        return milestones

    @staticmethod
    def generate_milestones(commits: List[Dict[str, Any]], releases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        
        creation = MilestoneDetector.detect_repository_creation(commits)
        if creation:
            creation["type"] = "project_creation"
            milestones.append(creation)
            
        milestones.extend(MilestoneDetector.detect_component_introductions(commits))
        milestones.extend(MilestoneDetector.detect_module_introductions(commits))
        milestones.extend(MilestoneDetector.detect_contributor_growth(commits))
        
        # Add releases as milestones
        for release in releases:
            date = release.get("published_at") or release.get("created_at")
            if date:
                milestones.append({
                    "date": date,
                    "type": "release",
                    "event_description": f"Release: {release.get('name') or release.get('tag_name')}"
                })
                
        # Sort milestones by date
        milestones.sort(key=lambda m: parse_date(m["date"]))
        return milestones

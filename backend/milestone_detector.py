import re
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Any
from utils import parse_date

class MilestoneDetector:
    @staticmethod
    def detect_repository_creation(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not commits:
            return {}
        
        valid_commits = [c for c in commits if c.get("date")]
        if not valid_commits:
            return {}
            
        valid_commits.sort(key=lambda x: parse_date(x["date"]))
        first = valid_commits[0]
        
        return {
            "type": "project_creation",
            "date": first["date"],
            "event_description": f"Repository created by {first.get('author')}."
        }

    @staticmethod
    def detect_architecture_shifts(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(commits) < 10:
            return []
            
        milestones = []
        sizes = [c.get("additions", 0) + c.get("deletions", 0) for c in commits]
        
        mean_size = statistics.mean(sizes)
        std_size = statistics.stdev(sizes)
        threshold = mean_size + 2.5 * std_size
        
        for commit in commits:
            size = commit.get("additions", 0) + commit.get("deletions", 0)
            files_changed = commit.get("files_changed", [])
            
            # Count unique top-level directories
            unique_dirs = set()
            for f in files_changed:
                if "/" in f:
                    unique_dirs.add(f.split("/")[0])
            
            if size > threshold and len(files_changed) >= 10 and len(unique_dirs) >= 3:
                milestones.append({
                    "type": "architecture_shift",
                    "date": commit["date"],
                    "event_description": "Large architectural change affecting multiple modules."
                })
        return milestones

    @staticmethod
    def detect_module_introductions(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        module_activity = defaultdict(int)
        module_first_seen = {}
        
        ignore_dirs = {"docs", "tests", ".github", "node_modules", "dist", "build", "assets", "public"}
        
        valid_commits = sorted([c for c in commits if c.get("date")], key=lambda x: parse_date(x["date"]))
        
        active_modules = set()
        
        for commit in valid_commits:
            files = commit.get("files", [])
            for f in files:
                status = f.get("status")
                filename = f.get("filename", "")
                
                if "/" in filename:
                    module = filename.split("/")[0]
                    if module in ignore_dirs:
                        continue
                        
                    if module not in module_first_seen:
                        module_first_seen[module] = commit["date"]
                    
                    if status == "added":
                        module_activity[module] += 1
                        
                        if module not in active_modules and module_activity[module] >= 5:
                            active_modules.add(module)
                            milestones.append({
                                "type": "module_introduction",
                                "module": module,
                                "date": commit["date"],
                                "event_description": f"New major module established: {module}."
                            })
        return milestones

    @staticmethod
    def detect_testing_adoption(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        # Group testing commits by month
        monthly_testing = defaultdict(int)
        
        valid_commits = sorted([c for c in commits if c.get("date")], key=lambda x: parse_date(x["date"]))
        
        for commit in valid_commits:
            if commit.get("type") == "testing":
                month = commit["date"][:7]
                monthly_testing[month] += 1
        
        sorted_months = sorted(monthly_testing.keys())
        for i, month in enumerate(sorted_months):
            if monthly_testing[month] >= 3:
                # Check if testing was inactive before
                prev_month = (datetime.strptime(month, "%Y-%m") - timedelta(days=28)).strftime("%Y-%m")
                if monthly_testing.get(prev_month, 0) == 0:
                    # Find first testing commit this month
                    first_test_commit = next(c for c in valid_commits if c["date"][:7] == month and c.get("type") == "testing")
                    milestones.append({
                        "type": "testing_adoption",
                        "date": first_test_commit["date"],
                        "event_description": "Automated testing practices introduced."
                    })
                    break # Only one testing adoption milestone
        return milestones

    @staticmethod
    def detect_contributor_growth(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        monthly_authors = defaultdict(set)
        
        for c in commits:
            if c.get("date") and c.get("author"):
                month = c["date"][:7]
                monthly_authors[month].add(c["author"])
                
        sorted_months = sorted(monthly_authors.keys())
        for i in range(1, len(sorted_months)):
            curr_month = sorted_months[i]
            curr_count = len(monthly_authors[curr_month])
            
            lookback = sorted_months[max(0, i-3):i]
            if not lookback:
                continue
                
            avg_prev = sum(len(monthly_authors[m]) for m in lookback) / len(lookback)
            
            if curr_count >= 2 * avg_prev and curr_count >= 4:
                milestones.append({
                    "type": "contributor_growth",
                    "date": curr_month + "-01T00:00:00Z",
                    "event_description": "Significant growth in project contributors."
                })
        return milestones

    @staticmethod
    def detect_development_bursts(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        weekly_commits = defaultdict(int)
        
        for c in commits:
            if c.get("date"):
                dt = parse_date(c["date"])
                # Get start of week (Monday)
                week_start = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
                weekly_commits[week_start] += 1
                
        if not weekly_commits:
            return []
            
        avg_weekly = statistics.mean(weekly_commits.values())
        
        for week, count in sorted(weekly_commits.items()):
            if count >= 2 * avg_weekly and count >= 10: # Minimum 10 commits for a "burst"
                milestones.append({
                    "type": "development_burst",
                    "date": week + "T00:00:00Z",
                    "event_description": "Major surge in development activity."
                })
        return milestones

    @staticmethod
    def detect_dependency_migration(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        weekly_deps = defaultdict(int)
        
        for c in commits:
            if c.get("date") and c.get("type") == "dependency":
                dt = parse_date(c["date"])
                week_start = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
                weekly_deps[week_start] += 1
                
        for week, count in sorted(weekly_deps.items()):
            if count >= 3:
                milestones.append({
                    "type": "dependency_migration",
                    "date": week + "T00:00:00Z",
                    "event_description": "Significant dependency or framework upgrade."
                })
        return milestones

    @staticmethod
    def detect_change_points(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        milestones = []
        weekly_commits = defaultdict(int)
        
        # Group by Monday start of week
        for c in commits:
            if c.get("date"):
                dt = parse_date(c["date"])
                week_start = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
                weekly_commits[week_start] += 1
                
        sorted_weeks = sorted(weekly_commits.keys())
        if len(sorted_weeks) < 5: # Need at least 4 weeks for baseline + 1 for current
            return []
            
        for i in range(4, len(sorted_weeks)):
            curr_week = sorted_weeks[i]
            curr_count = weekly_commits[curr_week]
            
            # Baseline: Average of previous 4 weeks
            prev_weeks = sorted_weeks[i-4:i]
            prev_avg = statistics.mean(weekly_commits[w] for w in prev_weeks)
            
            if prev_avg > 0:
                # 1. Phase Shift (Significant increase)
                if curr_count >= prev_avg * 2 and curr_count >= 10:
                    milestones.append({
                        "type": "development_phase_shift",
                        "date": curr_week + "T00:00:00Z",
                        "event_description": "Development activity significantly increased, indicating a new project phase."
                    })
                # 2. Slowdown (Significant drop)
                elif curr_count <= prev_avg * 0.5 and prev_avg >= 5: # Baseline needs to be non-trivial for "slowdown"
                    milestones.append({
                        "type": "development_slowdown",
                        "date": curr_week + "T00:00:00Z",
                        "event_description": "Development activity slowed significantly."
                    })
        return milestones

    @staticmethod
    def generate_milestones(commits: List[Dict[str, Any]], releases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        all_candidates = []
        
        creation = MilestoneDetector.detect_repository_creation(commits)
        if creation:
            all_candidates.append(creation)
            
        all_candidates.extend(MilestoneDetector.detect_architecture_shifts(commits))
        all_candidates.extend(MilestoneDetector.detect_module_introductions(commits))
        all_candidates.extend(MilestoneDetector.detect_testing_adoption(commits))
        all_candidates.extend(MilestoneDetector.detect_contributor_growth(commits))
        all_candidates.extend(MilestoneDetector.detect_development_bursts(commits))
        all_candidates.extend(MilestoneDetector.detect_dependency_migration(commits))
        all_candidates.extend(MilestoneDetector.detect_change_points(commits))
        
        for release in releases:
            date = release.get("published_at") or release.get("created_at")
            if date:
                all_candidates.append({
                    "date": date,
                    "type": "release",
                    "event_description": f"Release: {release.get('name') or release.get('tag_name')}"
                })
                
        # Weekly De-duplication and Sorting
        all_candidates.sort(key=lambda m: parse_date(m["date"]))
        
        final_milestones = []
        seen_weeks = defaultdict(set)
        
        for m in all_candidates:
            dt = parse_date(m["date"])
            week_id = f"{dt.year}-W{dt.isocalendar()[1]}"
            m_type = m["type"]
            
            # Allow multiple types per week, but deduplicate identical types
            if m_type not in seen_weeks[week_id]:
                final_milestones.append(m)
                seen_weeks[week_id].add(m_type)
                
        return sorted(final_milestones, key=lambda m: parse_date(m["date"]))

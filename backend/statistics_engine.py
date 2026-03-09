import math
import statistics
from collections import defaultdict
from typing import List, Dict, Any
from datetime import datetime
from utils import parse_date

class StatisticsEngine:
    @staticmethod
    def compute_commit_frequency(commits: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        weekly = defaultdict(int)
        monthly = defaultdict(int)
        
        for commit in commits:
            date_str = commit.get("date")
            if not date_str:
                continue
            dt = parse_date(date_str)
            week_str = f"{dt.year}-W{dt.strftime('%V')}"
            month_str = f"{dt.year}-{dt.strftime('%m')}"
            
            weekly[week_str] += 1
            monthly[month_str] += 1
            
        return {
            "commits_per_week": dict(weekly),
            "commits_per_month": dict(monthly)
        }
        
    @staticmethod
    def detect_bursts(commits_per_week: Dict[str, int]) -> List[str]:
        if not commits_per_week:
            return []
            
        counts = list(commits_per_week.values())
        if len(counts) < 2:
            return []
            
        mean = sum(counts) / len(counts)
        variance = sum((x - mean) ** 2 for x in counts) / len(counts)
        std_dev = math.sqrt(variance)
        
        bursts = []
        for week, count in commits_per_week.items():
            if count > mean + 2 * std_dev:
                bursts.append(week)
                
        return bursts
        
    @staticmethod
    def compute_impact_score(commit: Dict[str, Any]) -> int:
        """
        Improved Impact Score model:
        Uses log normalization for files_changed to prevent large-scale renames 
        or doc updates from dominating the score.
        """
        files_changed = len(commit.get("files_changed", []))
        additions = commit.get("additions", 0)
        deletions = commit.get("deletions", 0)
        
        # log(x+1) normalization ensures diminishing returns on the number of files
        log_normalization = math.log(files_changed + 1)
        impact = (additions + deletions) + (files_changed * log_normalization * 10)
        return int(impact)
        
    @staticmethod
    def detect_inactivity(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(commits) < 2:
            return []
            
        # Parse and sort dates
        dates = []
        for c in commits:
            d = c.get("date")
            if d:
                dates.append(parse_date(d))
        dates.sort()
        
        inactivity_periods = []
        for i in range(1, len(dates)):
            delta = (dates[i] - dates[i-1]).days
            if delta > 30:
                inactivity_periods.append({
                    "start": dates[i-1].isoformat(),
                    "end": dates[i].isoformat(),
                    "days": delta
                })
        return inactivity_periods
        
    @staticmethod
    def get_contributor_dominance(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not commits:
            return {}
            
        authors = defaultdict(int)
        for c in commits:
            author = c.get("author", "Unknown")
            authors[author] += 1
            
        total = sum(authors.values())
        if total == 0:
            return {}
            
        top_contributor = max(authors.items(), key=lambda x: x[1])
        dominance = top_contributor[1] / total
        
        return {
            "top_contributor": top_contributor[0],
            "commits": top_contributor[1],
            "total_commits": total,
            "dominance": dominance,
            "distribution": dict(authors)
        }
        
    @staticmethod
    def detect_hot_modules(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        modules = defaultdict(int)
        for commit in commits:
            files = commit.get("files_changed", [])
            for file_path in files:
                parts = file_path.split('/')
                if len(parts) > 1:
                    module = parts[0] + '/'
                    modules[module] += 1
                    
        # Sort and return top 10 as list for frontend
        sorted_modules = sorted(modules.items(), key=lambda item: item[1], reverse=True)[:10]
        return [{"module": m, "count": c} for m, c in sorted_modules]

    @staticmethod
    def detect_architecture_changes(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adaptive Architecture Change Detection:
        Threshold = Mean(Size) + 3 * StdDev(Size)
        Size = additions + deletions
        """
        if not commits:
            return []

        sizes = [c.get("additions", 0) + c.get("deletions", 0) for c in commits]
        if len(sizes) < 2:
            return []

        mean_size = statistics.mean(sizes)
        std_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
        threshold = mean_size + (3 * std_size)
        
        changes = []
        for c in commits:
            size = c.get("additions", 0) + c.get("deletions", 0)
            if size > threshold and size > 50: # Avoid noise on empty repos
                changes.append({
                    "sha": c.get("sha"),
                    "message": c.get("message"),
                    "date": c.get("date"),
                    "impact_score": StatisticsEngine.compute_impact_score(c),
                    "is_adaptive": True
                })
        return changes

    @staticmethod
    def calculate_bus_factor(commits: List[Dict[str, Any]]) -> int:
        """
        Bus Factor Calculation:
        Minimum number of contributors accounting for at least 50% of total commits.
        """
        if not commits:
            return 0
        
        authors = defaultdict(int)
        for c in commits:
            authors[c.get("author", "Unknown")] += 1
        
        sorted_authors = sorted(authors.values(), reverse=True)
        total_commits = len(commits)
        threshold = total_commits * 0.5
        
        count = 0
        cumulative = 0
        for commits_count in sorted_authors:
            cumulative += commits_count
            count += 1
            if cumulative >= threshold:
                break
        return count

    @staticmethod
    def calculate_collaboration_score(commits: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Improved Collaboration Intensity:
        CollaborationScore = UniqueAuthors_month / Commits_month
        """
        monthly_authors = defaultdict(set)
        monthly_commits = defaultdict(int)
        
        for c in commits:
            d = c.get("date")
            author = c.get("author")
            if d and author:
                # Use first 7 chars for YYYY-MM
                month_str = d[:7]
                monthly_authors[month_str].add(author)
                monthly_commits[month_str] += 1
                
        scores = {}
        for month in monthly_commits:
            score = len(monthly_authors[month]) / monthly_commits[month]
            scores[month] = round(score, 3)
            
        return scores

    @staticmethod
    def calculate_maturity_score(commits: List[Dict[str, Any]]) -> float:
        """
        Repository Maturity Score:
        (RefactorCommits + TestCommits) / TotalCommits
        Score > 0.30 indicates a mature codebase focus on stability/refinement.
        """
        if not commits:
            return 0.0
            
        special_commits = 0
        for c in commits:
            c_type = c.get("type", "other")
            message = c.get("message", "").lower()
            
            if c_type in ["refactor", "testing"]:
                special_commits += 1
            elif "refactor" in message or "test" in message:
                special_commits += 1
                
        return round(special_commits / len(commits), 3)

import math
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
        files_count = len(commit.get("files_changed", []))
        additions = commit.get("additions", 0)
        deletions = commit.get("deletions", 0)
        return files_count * 5 + additions + deletions
        
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
    def detect_hot_modules(commits: List[Dict[str, Any]]) -> Dict[str, int]:
        modules = defaultdict(int)
        for commit in commits:
            files = commit.get("files_changed", [])
            for file_path in files:
                parts = file_path.split('/')
                if len(parts) > 1:
                    module = parts[0] + '/'
                    modules[module] += 1
                    
        # Sort and return top 10
        sorted_modules = dict(sorted(modules.items(), key=lambda item: item[1], reverse=True)[:10])
        return sorted_modules

    @staticmethod
    def detect_architecture_changes(commits: List[Dict[str, Any]], threshold: int = 500) -> List[Dict[str, Any]]:
        changes = []
        for c in commits:
            impact = StatisticsEngine.compute_impact_score(c)
            if impact > threshold:
                changes.append({
                    "sha": c.get("sha"),
                    "message": c.get("message"),
                    "date": c.get("date"),
                    "impact_score": impact
                })
        return changes

    @staticmethod
    def analyze_contributor_impact(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates core maintainers and high-impact contributors based on commit frequency and total impact score."""
        contributor_stats = defaultdict(lambda: {"commits": 0, "impact_score": 0})
        
        for c in commits:
            author = c.get("author", "Unknown")
            contributor_stats[author]["commits"] += 1
            contributor_stats[author]["impact_score"] += StatisticsEngine.compute_impact_score(c)
            
        # Determine core vs occasional by finding those > 10% of total commits
        total_commits = len(commits)
        core_maintainers = []
        high_impact = []
        
        for author, stats in contributor_stats.items():
            if stats["commits"] / max(total_commits, 1) > 0.10:
                core_maintainers.append({"name": author, "commits": stats["commits"]})
                
        # Top 5 by impact score
        sorted_by_impact = sorted(contributor_stats.items(), key=lambda x: x[1]["impact_score"], reverse=True)
        for author, stats in sorted_by_impact[:5]:
            high_impact.append({"name": author, "impact_score": stats["impact_score"]})
            
        return {
            "core_maintainers": core_maintainers,
            "high_impact_contributors": high_impact
        }

    @staticmethod
    def analyze_code_ownership(commits: List[Dict[str, Any]]) -> Dict[str, str]:
        """Maps directory/module to the contributor who modifies it the most."""
        module_authors = defaultdict(lambda: defaultdict(int))
        
        for c in commits:
            author = c.get("author", "Unknown")
            for f in c.get("files_changed", []):
                parts = f.split('/')
                if len(parts) > 1:
                    module = parts[0] + '/'
                    module_authors[module][author] += 1
                    
        ownership = {}
        for module, authors_dict in module_authors.items():
            top_author = max(authors_dict.items(), key=lambda x: x[1])[0]
            ownership[module] = top_author
            
        return ownership

    @staticmethod
    def calculate_collaboration_intensity(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Measure what phases had the most unique contributors working simultaneously."""
        # Simple heuristic: Group commits by month, count unique authors
        monthly_authors = defaultdict(set)
        
        for c in commits:
            d = c.get("date")
            author = c.get("author")
            if d and author:
                dt = parse_date(d)
                month_str = f"{dt.year}-{dt.strftime('%m')}"
                monthly_authors[month_str].add(author)
                
        intensity = {month: len(authors) for month, authors in monthly_authors.items()}
        
        if not intensity:
            return {"peak_collaboration_month": None, "intensity_by_month": {}}
            
        peak_month = max(intensity.items(), key=lambda x: x[1])
        
        return {
            "peak_collaboration_month": peak_month[0],
            "peak_unique_contributors": peak_month[1],
            "intensity_by_month": intensity
        }

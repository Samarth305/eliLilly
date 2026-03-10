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
                # Ignore noise directories
                if file_path.startswith(("tests/", "docs/", ".github/")):
                    continue
                    
                parts = file_path.split('/')
                if len(parts) > 1:
                    module = parts[0] + '/'
                    modules[module] += 1
                    
        # Sort and return all hot modules
        sorted_modules = sorted(modules.items(), key=lambda item: item[1], reverse=True)
        return [{"module": m, "count": c} for m, c in sorted_modules]

    @staticmethod
    def detect_architecture_changes(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Architecture Shift Detection:
        Multi-signal thresholding based on size, files, directories, and message keywords.
        """
        if not commits:
            return []

        sizes = [c.get("additions", 0) + c.get("deletions", 0) for c in commits]
        if len(sizes) < 2:
            return []

        mean_size = statistics.mean(sizes)
        std_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
        # Lower threshold to 2.5 sigma for better recall
        size_threshold = mean_size + (2.5 * std_size)

        refactor_keywords = ["refactor", "rewrite", "restructure", "migrate"]
        
        changes = []
        for c in commits:
            size = c.get("additions", 0) + c.get("deletions", 0)
            files = c.get("files", [])
            
            # Condition 1: Size
            cond_size = size > size_threshold
            
            # Condition 2: Files changed
            cond_files = len(files) >= 10
            
            # Condition 3: Unique directories
            dirs = set()
            for f in files:
                filename = f.get("filename", "")
                if "/" in filename:
                    dirs.add(filename[:filename.rfind("/")])
            cond_dirs = len(dirs) >= 3
            
            # Condition 4: Refactor keywords
            message = c.get("message", "").lower()
            cond_keywords = any(kw in message for kw in refactor_keywords)
            
            # Strict multi-signal rule
            if cond_size and cond_files and cond_dirs and cond_keywords:
                changes.append({
                    "type": "architecture_shift",
                    "commit_sha": c.get("sha"),
                    "date": c.get("date"),
                    "impact": size
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
            total_commits = monthly_commits[month]
            if total_commits >= 10:
                score = len(monthly_authors[month]) / math.sqrt(total_commits)
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

    @staticmethod
    def calculate_commit_distribution(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculate the distribution of commits across different categories.
        """
        distribution = defaultdict(int)
        for c in commits:
            category = c.get("type", "other")
            distribution[category] += 1
            
        return [{"category": k, "count": v} for k, v in sorted(distribution.items(), key=lambda x: x[1], reverse=True)]

    @staticmethod
    def calculate_efficiency_index(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Efficiency Index Calculation:
        Efficiency = 100 * Velocity * Quality
        Velocity = Commits_last_month / Avg_monthly_commits
        Quality = (Feature + Refactor + Performance) / TotalCommits
        """
        if not commits:
            return {"efficiency": 0.0, "velocity": 0.0, "quality": 0.0}
            
        # 1. Calculate Quality
        quality_types = ["feature", "refactor", "performance"]
        quality_count = sum(1 for c in commits if c.get("type") in quality_types)
        quality = quality_count / len(commits)
        
        # 2. Calculate Velocity
        monthly_commits = defaultdict(int)
        for c in commits:
            d = c.get("date")
            if d:
                month_str = d[:7] # YYYY-MM
                monthly_commits[month_str] += 1
        
        if not monthly_commits:
            return {"efficiency": 0.0, "velocity": 0.0, "quality": round(quality, 3)}
            
        sorted_months = sorted(monthly_commits.keys())
        last_month_commits = monthly_commits[sorted_months[-1]]
        avg_monthly_commits = sum(monthly_commits.values()) / len(monthly_commits)
        
        velocity = last_month_commits / avg_monthly_commits if avg_monthly_commits > 0 else 0
        velocity = min(velocity, 2.0)
        
        # 3. Final Efficiency (Log-sqrt stabilization)
        efficiency = 100 * math.sqrt(velocity) * quality
        
        return {
            "score": round(efficiency, 2),
            "velocity": round(velocity, 2),
            "quality": round(quality, 3)
        }

    @staticmethod
    def calculate_momentum(commits: List[Dict[str, Any]]) -> float:
        """
        Momentum = commits_last_30_days / commits_previous_30_days
        """
        if not commits:
            return 0.0
            
        now = datetime.now() # In real usage this would correlate with repo's last commit date or current time
        last_30 = 0
        prev_30 = 0
        
        # Use commit dates to calculate relative momentum
        for c in commits:
            d_str = c.get("date")
            if not d_str:
                continue
            try:
                dt = parse_date(d_str).replace(tzinfo=None)
                days_ago = (now - dt).days
                
                if days_ago <= 30:
                    last_30 += 1
                elif 31 <= days_ago <= 60:
                    prev_30 += 1
            except:
                continue
                
        if prev_30 == 0:
            return float(last_30) if last_30 > 0 else 1.0
            
        return round(last_30 / prev_30, 2)

    @staticmethod
    def detect_development_phases(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Lightweight Clustering for Development Phases.
        Extracts dominant commit types, top modules, unique contributors, and avg commit size.
        """
        if not commits:
            return []
            
        # 1. Group commits by week
        weekly_commits_map = defaultdict(list)
        for commit in commits:
            date_str = commit.get("date")
            if not date_str:
                continue
            dt = parse_date(date_str)
            week_str = f"{dt.year}-W{dt.strftime('%V')}"
            weekly_commits_map[week_str].append(commit)
            
        if not weekly_commits_map:
            return []
            
        # 2. Compute mean weekly commit activity
        counts = [len(c_list) for c_list in weekly_commits_map.values()]
        avg_commits = statistics.mean(counts)
        
        # 3. Detect active weeks
        sorted_weeks = sorted(weekly_commits_map.keys())
        active_weeks = []
        for week in sorted_weeks:
            if len(weekly_commits_map[week]) >= avg_commits:
                active_weeks.append(week)
                
        # 4. Merge consecutive active weeks
        if not active_weeks:
            return []
            
        def compute_phase_stats(phase_start, phase_end, week_list):
            phase_commits = []
            for w in week_list:
                phase_commits.extend(weekly_commits_map[w])
                
            types = defaultdict(int)
            modules = defaultdict(int)
            authors = set()
            total_size = 0
            
            for c in phase_commits:
                c_type = c.get("type", "other")
                types[c_type] += 1
                authors.add(c.get("author", "Unknown"))
                total_size += (c.get("additions", 0) + c.get("deletions", 0))
                
                # Top modules calculation
                for f in c.get("files_changed", []):
                    parts = f.split('/')
                    if len(parts) > 1:
                        modules[parts[0]] += 1
                        
            dominant_type = max(types.items(), key=lambda x: x[1])[0] if types else "other"
            top_modules = [m[0] for m in sorted(modules.items(), key=lambda x: x[1], reverse=True)[:3]]
            avg_size = total_size // len(phase_commits) if phase_commits else 0
            
            return {
                "start": phase_start,
                "end": phase_end,
                "commit_count": len(phase_commits),
                "dominant_commit_type": dominant_type,
                "top_modules": top_modules,
                "contributors": len(authors),
                "avg_commit_size": avg_size,
                "phase_type": "active_development_phase"
            }
            
        phases = []
        current_start = active_weeks[0]
        current_end = active_weeks[0]
        current_weeks = [active_weeks[0]]
        
        for i in range(1, len(active_weeks)):
            prev_week = active_weeks[i-1]
            curr_week = active_weeks[i]
            
            # Simple check for consecutive weeks (e.g., 2024-W05 to 2024-W06)
            y1, w1 = map(int, prev_week.split('-W'))
            y2, w2 = map(int, curr_week.split('-W'))
            
            is_consecutive = (y1 == y2 and w2 - w1 == 1) or (y2 - y1 == 1 and w2 == 1 and w1 in [52, 53])
            
            if is_consecutive:
                current_end = curr_week
                current_weeks.append(curr_week)
            else:
                phases.append(compute_phase_stats(current_start, current_end, current_weeks))
                current_start = curr_week
                current_end = curr_week
                current_weeks = [curr_week]
                
        # Append the last phase
        phases.append(compute_phase_stats(current_start, current_end, current_weeks))
        
        return phases

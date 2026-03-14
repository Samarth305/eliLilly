import math
import statistics
from collections import defaultdict
from typing import List, Dict, Any
from datetime import datetime
from utils import parse_date

class StatisticsEngine:
    @staticmethod
    def _calculate_impact(additions: int, deletions: int, files_changed: int) -> int:
        """
        Reusable impact score formula:
        impact = (additions + deletions) + (files_changed * ln(files_changed + 1) * 10)
        """
        log_normalization = math.log(files_changed + 1)
        impact = (additions + deletions) + (files_changed * log_normalization * 10)
        return int(impact)

    @staticmethod
    def _extract_module(file_path: str) -> str:
        """
        Extract module name from file path, ignoring noise directories.
        """
        noise = ("tests/", "docs/", ".github/", "node_modules/", "dist/", "build/", "vendor/")
        if file_path.startswith(noise):
            return ""
        
        parts = file_path.split('/')
        if len(parts) > 1:
            return parts[0] + '/'
        return ""

    @staticmethod
    def _get_module_analytics(commits: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Single-pass O(N) collection of module-level statistics.
        Returns a dictionary mapping module names to their stats.
        """
        module_stats = defaultdict(lambda: {
            "commits": 0,
            "total_impact": 0,
            "total_churn": 0,
            "authors": defaultdict(int)
        })

        for commit in commits:
            additions = commit.get("additions", 0)
            deletions = commit.get("deletions", 0)
            files = commit.get("files_changed", [])
            author = commit.get("author", "Unknown")
            
            impact = StatisticsEngine._calculate_impact(additions, deletions, len(files))
            churn = additions + deletions
            
            seen_modules = set()
            for file_path in files:
                module = StatisticsEngine._extract_module(file_path)
                if module and module not in seen_modules:
                    stats = module_stats[module]
                    stats["commits"] += 1
                    stats["total_impact"] += impact
                    stats["total_churn"] += churn
                    stats["authors"][author] += 1
                    seen_modules.add(module)
                    
        return module_stats

    @staticmethod
    def _get_sorted_commits(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Pre-parse dates and sort commits chronologically.
        Adds a parsed_dt field to each commit.
        """
        parsed_commits = []
        for c in commits:
            date_str = c.get("date")
            if date_str:
                dt = parse_date(date_str)
                # Ensure dt is offset-naive if comparing with datetime.now()
                if dt.tzinfo:
                    dt = dt.replace(tzinfo=None)
                c_copy = c.copy()
                c_copy["parsed_dt"] = dt
                parsed_commits.append(c_copy)
        
        return sorted(parsed_commits, key=lambda x: x["parsed_dt"])

    @staticmethod
    def compute_commit_frequency(commits: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
        weekly = defaultdict(int)
        monthly = defaultdict(int)
        
        sorted_commits = StatisticsEngine._get_sorted_commits(commits)
        
        for commit in sorted_commits:
            dt = commit["parsed_dt"]
            # ISO week standard (%G-W%V)
            week_str = dt.strftime('%G-W%V')
            month_str = dt.strftime('%Y-%m')
            
            weekly[week_str] += 1
            monthly[month_str] += 1
            
        return {
            "commits_per_week": dict(weekly),
            "commits_per_month": dict(monthly)
        }
        
    @staticmethod
    def detect_bursts(commits_per_week: Dict[str, int]) -> List[Dict[str, Any]]:
        if not commits_per_week or len(commits_per_week) < 8:
            return []
            
        counts = list(commits_per_week.values())
        mean = statistics.mean(counts)
        std_dev = statistics.stdev(counts)
        threshold = mean + 2 * std_dev
        
        bursts = []
        for week, count in commits_per_week.items():
            if count > threshold:
                bursts.append({
                    "week": week,
                    "commit_count": count,
                    "threshold": round(threshold, 2)
                })
                
        return bursts
        
    @staticmethod
    def compute_impact_score(commit: Dict[str, Any]) -> int:
        """
        Improved Impact Score model using the central helper.
        """
        additions = commit.get("additions", 0)
        deletions = commit.get("deletions", 0)
        files_changed = len(commit.get("files_changed", []))
        
        return StatisticsEngine._calculate_impact(additions, deletions, files_changed)
        
    @staticmethod
    def detect_inactivity(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(commits) < 2:
            return []
            
        sorted_commits = StatisticsEngine._get_sorted_commits(commits)
        dates = [c["parsed_dt"] for c in sorted_commits]
        
        inactivity_periods = []
        for i in range(1, len(dates)):
            delta = (dates[i] - dates[i-1]).days
            if delta > 45:
                severity = "severe" if delta > 90 else "moderate"
                inactivity_periods.append({
                    "start": dates[i-1].isoformat(),
                    "end": dates[i].isoformat(),
                    "days": delta,
                    "severity": severity
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
        """
        Advanced Hotspot Detection:
        Formula: hotspot_score = commit_count * average_impact
        Incorporate churn signals for criticality flags.
        """
        module_stats = StatisticsEngine._get_module_analytics(commits)
        
        hot_modules = []
        for module, stats in module_stats.items():
            avg_impact = stats["total_impact"] / stats["commits"]
            hotspot_score = stats["commits"] * avg_impact
            
            # Incorporate churn signal
            avg_churn = stats["total_churn"] / stats["commits"]
            is_critical = hotspot_score > 1000 and avg_churn > 500 # Thresholds for "critical"
            
            hot_modules.append({
                "module": module,
                "commits": stats["commits"],
                "count": stats["commits"],  # Added for frontend compatibility
                "avg_impact": round(avg_impact, 2),
                "churn": stats["total_churn"],
                "hotspot_score": round(hotspot_score, 2),
                "is_critical": is_critical
            })
            
        return sorted(hot_modules, key=lambda x: x["hotspot_score"], reverse=True)

    @staticmethod
    def analyze_code_churn(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Code Churn Analysis:
        Measures instability of modules based on total additions + deletions.
        """
        module_stats = StatisticsEngine._get_module_analytics(commits)
        churn_list = []
        
        # Calculate thresholds for instability
        all_churns = [s["total_churn"] for s in module_stats.values()]
        if not all_churns: return []
        
        mean_churn = statistics.mean(all_churns)
        std_churn = statistics.stdev(all_churns) if len(all_churns) > 1 else 0
        unstable_threshold = mean_churn + 2 * std_churn
        
        for module, stats in module_stats.items():
            avg_churn = stats["total_churn"] / stats["commits"]
            churn_list.append({
                "module": module,
                "commits": stats["commits"],
                "churn": stats["total_churn"],
                "avg_churn_per_commit": round(avg_churn, 2),
                "is_unstable": stats["total_churn"] > unstable_threshold
            })
            
        return sorted(churn_list, key=lambda x: x["churn"], reverse=True)

    @staticmethod
    def detect_knowledge_silos(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Knowledge Silo Detection:
        Detects modules dominated by a single contributor.
        """
        module_stats = StatisticsEngine._get_module_analytics(commits)
        silos = []
        
        for module, stats in module_stats.items():
            total_module_commits = stats["commits"]
            if total_module_commits == 0: continue
            
            authors = stats["authors"]
            top_contributor = max(authors.items(), key=lambda x: x[1])
            ownership_ratio = top_contributor[1] / total_module_commits
            
            risk_level = "low"
            if ownership_ratio > 0.7:
                risk_level = "high"
            elif ownership_ratio > 0.5:
                risk_level = "moderate"
                
            silos.append({
                "module": module,
                "top_contributor": top_contributor[0],
                "ownership_ratio": round(ownership_ratio, 3),
                "risk_level": risk_level
            })
            
        return sorted(silos, key=lambda x: x["ownership_ratio"], reverse=True)

    @staticmethod
    def detect_architecture_changes(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Architecture Shift Detection:
        Multi-signal thresholding based on size, files, directories, and message keywords.
        Enhanced with hotspot and churn signals.
        """
        if not commits:
            return []

        # Get hotspot info to enhance detection
        hotspots = {h["module"]: h for h in StatisticsEngine.detect_hot_modules(commits)}

        sizes = [c.get("additions", 0) + c.get("deletions", 0) for c in commits]
        if len(sizes) < 2:
            return []

        mean_size = statistics.mean(sizes)
        std_size = statistics.stdev(sizes)
        size_threshold = mean_size + (2.5 * std_size)

        refactor_keywords = ["refactor", "rewrite", "restructure", "migrate"]
        
        changes = []
        for c in commits:
            size = c.get("additions", 0) + c.get("deletions", 0)
            files = c.get("files_changed", [])
            
            cond_size = size > size_threshold
            cond_files = len(files) >= 10
            
            dirs = set()
            affected_hotspots = 0
            for f_path in files:
                if "/" in f_path:
                    dirs.add(f_path[:f_path.rfind("/")])
                
                module = StatisticsEngine._extract_module(f_path)
                if module in hotspots and hotspots[module]["is_critical"]:
                    affected_hotspots += 1
                    
            cond_dirs = len(dirs) >= 3
            message = c.get("message", "").lower()
            keyword_match = any(kw in message for kw in refactor_keywords)
            
            # Confidence score calculation
            score = 0.4 
            if cond_size: score += 0.2
            if cond_files: score += 0.1
            if cond_dirs: score += 0.1
            if keyword_match: score += 0.1
            if affected_hotspots > 0: score += 0.1 # Hotspot integration
            
            if cond_size and cond_files and cond_dirs:
                changes.append({
                    "type": "architecture_shift",
                    "sha": c.get("sha"),
                    "message": c.get("message"),
                    "date": c.get("date"),
                    "impact_score": size,
                    "directories_changed": len(dirs),
                    "confidence": round(min(score, 1.0), 2),
                    "affected_hotspots": affected_hotspots
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
    def calculate_collaboration_score(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Improved Collaboration Intensity:
        Calculation: UniqueAuthors / sqrt(Commits)
        Filter: Ignore months with fewer than 10 commits.
        """
        monthly_authors = defaultdict(set)
        monthly_commits = defaultdict(int)
        
        for c in commits:
            d = c.get("date")
            author = c.get("author")
            if d and author:
                month_str = d[:7] # YYYY-MM
                monthly_authors[month_str].add(author)
                monthly_commits[month_str] += 1
                
        results = []
        for month in sorted(monthly_commits.keys()):
            commit_count = monthly_commits[month]
            if commit_count >= 10:
                unique_authors = len(monthly_authors[month])
                score = unique_authors / math.sqrt(commit_count)
                results.append({
                    "month": month,
                    "unique_authors": unique_authors,
                    "commits": commit_count,
                    "score": round(score, 3)
                })
            
        return results

    @staticmethod
    def calculate_maturity_score(commits: List[Dict[str, Any]]) -> float:
        """
        Improved Repository Maturity Score:
        (refactor + testing + performance + documentation) / total_commits
        """
        if not commits:
            return 0.0
            
        special_types = ["refactor", "testing", "performance", "documentation"]
        special_commits = 0
        for c in commits:
            c_type = c.get("type", "other")
            message = c.get("message", "").lower()
            
            if c_type in special_types:
                special_commits += 1
            elif any(kw in message for kw in special_types) or "test" in message:
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
        Improved Efficiency Index:
        Efficiency = 100 * sqrt(Velocity) * Quality
        Velocity = avg_commits_last_2_months / avg_monthly_commits (clamped 0-2)
        Quality = BaseQuality * (1 - ChurnPenalty)
        """
        if not commits:
            return {"score": 0.0, "velocity": 0.0, "quality": 0.0}
            
        # Get churn data for penalty
        churn_data = StatisticsEngine.analyze_code_churn(commits)
        unstable_count = sum(1 for m in churn_data if m["is_unstable"])
        churn_penalty = (unstable_count / len(churn_data)) * 0.2 if churn_data else 0
        
        # 1. Calculate Quality
        quality_types = ["feature", "refactor", "performance", "testing"]
        quality_count = sum(1 for c in commits if c.get("type") in quality_types)
        base_quality = quality_count / len(commits)
        quality = max(0.0, base_quality * (1 - churn_penalty))
        
        # 2. Calculate Velocity
        monthly_commits = defaultdict(int)
        for c in commits:
            d = c.get("date")
            if d:
                month_str = d[:7] # YYYY-MM
                monthly_commits[month_str] += 1
        
        if not monthly_commits:
            return {"score": 0.0, "velocity": 0.0, "quality": round(quality, 3)}
            
        sorted_months = sorted(monthly_commits.keys())
        last_2_months = sorted_months[-2:]
        avg_last_2 = sum(monthly_commits[m] for m in last_2_months) / len(last_2_months)
        avg_overall = sum(monthly_commits.values()) / len(monthly_commits)
        
        velocity = avg_last_2 / avg_overall if avg_overall > 0 else 0
        velocity = max(0.0, min(velocity, 2.0))
        
        # 3. Final Efficiency
        efficiency = 100 * math.sqrt(velocity) * quality
        
        return {
            "score": round(efficiency, 2),
            "velocity": round(velocity, 2),
            "quality": round(quality, 3),
            "churn_penalty": round(churn_penalty, 3)
        }

    @staticmethod
    def calculate_momentum(commits: List[Dict[str, Any]]) -> float:
        """
        Improved Momentum:
        Momentum = commits_last_30_days / commits_previous_30_days
        Reference date is the latest commit date in the dataset.
        """
        if not commits:
            return 0.0
            
        sorted_commits = StatisticsEngine._get_sorted_commits(commits)
        if not sorted_commits:
             return 0.0
             
        latest_date = sorted_commits[-1]["parsed_dt"]
        
        last_30 = 0
        prev_30 = 0
        
        for c in sorted_commits:
            dt = c["parsed_dt"]
            days_ago = (latest_date - dt).days
            
            if days_ago <= 30:
                last_30 += 1
            elif 31 <= days_ago <= 60:
                prev_30 += 1
                
        if prev_30 == 0:
            return float(last_30) if last_30 > 0 else 1.0
            
        return round(last_30 / prev_30, 2)

    @staticmethod
    def detect_development_phases(commits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Improved Clustering for Development Phases:
        - Sorted commits chronologically.
        - Minimum phase duration of 2 weeks.
        - Limit to top 5 most significant phases.
        """
        if not commits:
            return []
            
        sorted_commits = StatisticsEngine._get_sorted_commits(commits)
        
        # 1. Group commits by week
        weekly_commits_map = defaultdict(list)
        for commit in sorted_commits:
            dt = commit["parsed_dt"]
            week_str = dt.strftime('%G-W%V')
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
                
        if not active_weeks:
            return []
            
        def compute_phase_stats(week_list):
            phase_commits = []
            for w in week_list:
                phase_commits.extend(weekly_commits_map[w])
            
            # Get phase-specific module analytics
            phase_module_stats = StatisticsEngine._get_module_analytics(phase_commits)
                
            types = defaultdict(int)
            authors = set()
            total_size = 0
            total_impact = 0
            total_churn = 0
            
            unstable_modules = []
            siloed_modules = []
            
            for module, stats in phase_module_stats.items():
                total_churn += stats["total_churn"]
                
                # Check for unstable/silo modules within this phase context
                if stats["total_churn"] > 500: # Phase-local threshold
                    unstable_modules.append(module)
                
                top_author_commits = max(stats["authors"].values())
                if top_author_commits / stats["commits"] > 0.7:
                    siloed_modules.append(module)

            for c in phase_commits:
                additions = c.get("additions", 0)
                deletions = c.get("deletions", 0)
                files = c.get("files_changed", [])
                
                c_type = c.get("type", "other")
                types[c_type] += 1
                authors.add(c.get("author", "Unknown"))
                
                size = additions + deletions
                impact = StatisticsEngine._calculate_impact(additions, deletions, len(files))
                
                total_size += size
                total_impact += impact
                        
            dominant_type = max(types.items(), key=lambda x: x[1])[0] if types else "other"
            top_modules_list = [m[0] for m in sorted(phase_module_stats.items(), key=lambda x: x[1]["commits"], reverse=True)[:3]]
            avg_size = total_size // len(phase_commits) if phase_commits else 0
            avg_impact = total_impact / len(phase_commits) if phase_commits else 0
            
            return {
                "start": week_list[0],
                "end": week_list[-1],
                "weeks_duration": len(week_list),
                "commit_count": len(phase_commits),
                "dominant_commit_type": dominant_type,
                "top_modules": top_modules_list,
                "unstable_modules": unstable_modules[:3], # Limit noise
                "knowledge_silos": siloed_modules[:3],
                "contributors": len(authors),
                "avg_commit_size": avg_size,
                "avg_impact": round(avg_impact, 2),
                "phase_type": "active_development_phase"
            }
            
        phases = []
        current_weeks = [active_weeks[0]] if active_weeks else []
        
        for i in range(1, len(active_weeks)):
            prev_week = active_weeks[i-1]
            curr_week = active_weeks[i]
            
            # Consecutive weeks check
            y1, w1 = map(int, prev_week.split('-W'))
            y2, w2 = map(int, curr_week.split('-W'))
            is_consecutive = (y1 == y2 and w2 - w1 == 1) or (y2 - y1 == 1 and w2 == 1 and w1 in [52, 53])
            
            if is_consecutive:
                current_weeks.append(curr_week)
            else:
                # Close current phase
                # Heuristic: 2+ weeks, OR 1 week if it has > 1.5x the average complexity
                if len(current_weeks) >= 2:
                    phases.append(compute_phase_stats(current_weeks))
                elif len(current_weeks) == 1:
                    week_commits = weekly_commits_map[current_weeks[0]]
                    if len(week_commits) >= avg_commits * 1.5 or len(week_commits) > 5:
                        phases.append(compute_phase_stats(current_weeks))
                current_weeks = [curr_week]
                
        if current_weeks:
            if len(current_weeks) >= 2:
                phases.append(compute_phase_stats(current_weeks))
            elif len(current_weeks) == 1:
                week_commits = weekly_commits_map[current_weeks[0]]
                if len(week_commits) >= avg_commits * 1.5 or len(week_commits) > 5:
                    phases.append(compute_phase_stats(current_weeks))
            
        # Sort phases by significance (commit_count) and limit to top 5
        significant_phases = sorted(phases, key=lambda x: x["commit_count"], reverse=True)[:5]
        
        # Sort them back chronologically for the final output
        return sorted(significant_phases, key=lambda x: x["start"])
    @staticmethod
    def sample_commits(commits: List[Dict[str, Any]], target_total: int = 500) -> List[Dict[str, Any]]:
        """
        Smart Sampling Strategy:
        1. Genesis: First 50 commits (Origins)
        2. Evolution: Latest 300 commits (Current state)
        3. High Impact: Top 150 intermediate commits (Architectural shifts)
        """
        if len(commits) <= target_total:
            return commits

        # Ensure they are sorted for slicing
        # We don't use _get_sorted_commits because we don't want to re-parse everything yet if possible
        # But we need some order. Let's assume input raw nodes from GraphQL are latest-first or we sort them.
        # Actually GraphQL 'history' with 'first' is latest first.
        
        # Latest 300
        latest_300 = commits[:300]
        
        # First 50 (Genesis)
        remaining_after_latest = commits[300:]
        if len(remaining_after_latest) <= 200:
            return commits # Just return all if we are close to the limit
            
        genesis_50 = remaining_after_latest[-50:]
        
        # Intermediate 150 (High Impact)
        intermediate = remaining_after_latest[:-50]
        
        # Sort intermediate by impact (additions + deletions)
        def get_impact(c):
            return c.get("additions", 0) + c.get("deletions", 0)
            
        high_impact_intermediate = sorted(intermediate, key=get_impact, reverse=True)[:150]
        
        # Combine and deduplicate just in case
        sampled_shas = set()
        sampled_commits = []
        
        for c in (latest_300 + genesis_50 + high_impact_intermediate):
            sha = c.get("oid") or c.get("sha")
            if sha not in sampled_shas:
                sampled_shas.add(sha)
                sampled_commits.append(c)
                
        # Return them sorted chronologically for the analysis engine
        # We'll use the date string for a simple sort since we haven't parsed objects yet
        return sorted(sampled_commits, key=lambda x: x.get("committedDate") or x.get("date") or "")

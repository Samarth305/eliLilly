import datetime
import math
from typing import List, Dict, Any
from collections import defaultdict

class ContributorAnalyzer:
    @staticmethod
    def analyze(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Main entry point to run all contributor-related analyses.
        """
        if not commits:
            return {
                "core_maintainers": [],
                "high_impact_contributors": [],
                "contribution_patterns": {},
                "code_ownership": {},
                "collaboration_intensity": {}
            }

        # total_commits computed later via sum of values
        contributor_commits = defaultdict(int)
        contributor_impact = defaultdict(int)
        contribution_patterns = defaultdict(lambda: defaultdict(int))
        code_ownership = defaultdict(lambda: defaultdict(int))
        monthly_contributors = defaultdict(set)

        for commit in commits:
            author = commit.get("author", "Unknown")
            date_str = commit.get("date", "")
            
            # Simple parsing for month (YYYY-MM)
            # Format usually ISO: 2023-01-01T...
            month = date_str[:7] if len(date_str) >= 7 else "unknown"

            # 1 & 2. Stats per contributor
            contributor_commits[author] += 1
            
            # Impact Score Calculation (Normalized)
            files_changed = commit.get("files_changed", [])
            additions = commit.get("additions", 0)
            deletions = commit.get("deletions", 0)
            
            # Using the same log-normalized formula as StatisticsEngine
            num_files = len(files_changed)
            log_normalization = math.log(num_files + 1)
            impact = (additions + deletions) + (num_files * log_normalization * 10)
            contributor_impact[author] += int(impact)

            # 3. Patterns over time
            if month != "unknown":
                contribution_patterns[author][month] += 1
                # 5. Collaboration Intensity
                monthly_contributors[month].add(author)

            # 4. Code Ownership
            files = commit.get("files", [])
            for f in files:
                filename = f.get("filename", "")
                
                # Ignore noise directories for ownership computation
                if filename.startswith(("tests/", "docs/", ".github/")):
                    continue
                    
                if "/" in filename:
                    module = filename.split("/")[0]
                else:
                    module = "root"
                code_ownership[author][module] += 1

        # Finalizing Core Maintainers (Bus-factor style: 50% of commits)
        total_commits = sum(contributor_commits.values())
        sorted_contributors = sorted(contributor_commits.items(), key=lambda x: x[1], reverse=True)
        
        core_maintainers = []
        cumulative_commits = 0
        threshold = total_commits * 0.5
        
        for author, count in sorted_contributors:
            cumulative_commits += count
            ratio = count / total_commits
            core_maintainers.append({
                "name": author,
                "commits": count,
                "share": round(ratio, 3)
            })
            if cumulative_commits >= threshold:
                break

        # Finalizing High Impact
        high_impact = []
        for author, score in contributor_impact.items():
            high_impact.append({
                "name": author,
                "total_impact": score
            })
        high_impact.sort(key=lambda x: x["total_impact"], reverse=True)

        # Finalizing Collaboration Intensity: UniqueAuthors_month / sqrt(Commits_month)
        collaboration_intensity = {}
        monthly_commit_counts = defaultdict(int)
        for c in commits:
            d = c.get("date", "")
            if d:
                month = d[:7] if len(d) >= 7 else "unknown"
                monthly_commit_counts[month] += 1
                
        for month, authors in monthly_contributors.items():
            commits_in_month = monthly_commit_counts[month]
            if commits_in_month > 0:
                score = len(authors) / math.sqrt(commits_in_month)
                collaboration_intensity[month] = round(score, 3)

        return {
            "core_maintainers": core_maintainers,
            "high_impact_contributors": high_impact,
            "contribution_patterns": {k: dict(v) for k, v in contribution_patterns.items()},
            "code_ownership": {k: dict(v) for k, v in code_ownership.items()},
            "collaboration_intensity": collaboration_intensity
        }

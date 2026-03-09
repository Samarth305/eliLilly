import datetime
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

        total_commits = len(commits)
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
            month = date_str[:7] if len(date_str) >= 7 else "Unknown"

            # 1 & 2. Stats per contributor
            contributor_commits[author] += 1
            
            # Impact Score Calculation
            files_changed = commit.get("files_changed", [])
            additions = commit.get("additions", 0)
            deletions = commit.get("deletions", 0)
            impact = (len(files_changed) * 5) + additions + deletions
            contributor_impact[author] += impact

            # 3. Patterns over time
            if month != "Unknown":
                contribution_patterns[author][month] += 1
                # 5. Collaboration Intensity
                monthly_contributors[month].add(author)

            # 4. Code Ownership
            # Extract top-level directory from files if available
            # Note: CommitAnalyzer.extract_summary usually doesn't include file list by default
            # unless we modify it or pass details. 
            # Looking at existing architecture, 'detailed_commits' might have 'files' if we fetched them.
            # Assuming 'files' is a list of dicts with 'filename'
            files = commit.get("files", [])
            for f in files:
                filename = f.get("filename", "")
                if "/" in filename:
                    module = filename.split("/")[0]
                else:
                    module = "root"
                code_ownership[author][module] += 1

        # Finalizing Core Maintainers
        core_maintainers = []
        for author, count in contributor_commits.items():
            ratio = count / total_commits
            if ratio >= 0.2:
                core_maintainers.append({
                    "name": author,
                    "commits": count,
                    "ratio": round(ratio, 2)
                })

        # Finalizing High Impact
        high_impact = []
        for author, score in contributor_impact.items():
            high_impact.append({
                "name": author,
                "total_impact": score
            })
        high_impact.sort(key=lambda x: x["total_impact"], reverse=True)

        # Finalizing Collaboration Intensity
        collaboration_intensity = {
            month: len(authors) for month, authors in monthly_contributors.items()
        }

        return {
            "core_maintainers": core_maintainers,
            "high_impact_contributors": high_impact[:10], # Top 10
            "contribution_patterns": {k: dict(v) for k, v in contribution_patterns.items()},
            "code_ownership": {k: dict(v) for k, v in code_ownership.items()},
            "collaboration_intensity": collaboration_intensity
        }

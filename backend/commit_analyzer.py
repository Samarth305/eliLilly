import re
from typing import Dict, Any, Tuple

class CommitAnalyzer:
    # --- Keyword Dictionaries ---
    KEYWORDS = {
        "feature": [r'\badd\b', r'\bimplement\b', r'\bfeature\b', r'\bfeat\b', r'\bintroduce\b', r'\bcreate\b', r'\bsupport\b', r'\benable\b', r'\binit\b', r'\bsetup\b', r'\bscaffold\b', r'\bbootstrap\b', r'\bextend\b', r'\bstart\b'],
        "bugfix": [r'\bfix\b', r'\bbug\b', r'\bresolve\b', r'\bpatch\b', r'\bhotfix\b', r'\bcorrect\b', r'\brepair\b', r'\bissue\b', r'\berror\b', r'\bfail\b', r'\bhandle\b', r'\bprevent\b', r'\bavoid\b', r'\bcrash\b', r'\bfault\b'],
        "refactor": [r'\brefactor\b', r'\bcleanup\b', r'\brewrite\b', r'\brestructure\b', r'\bsimplify\b', r'\brename\b', r'\bimprove\b', r'\borganize\b', r'\bstructure\b', r'\bformat\b', r'\bsplit\b', r'\bmerge\b', r'cleanup unused'],
        "performance": [r'\boptimize\b', r'\bperf\b', r'\bperformance\b', r'\bspeed\b', r'\bfaster\b', r'\blatency\b', r'\bcache\b', r'\bmemory\b', r'\bcpu\b', r'\bopt\b', r'\bthroughput\b'],
        "testing": [r'\btest\b', r'\btests\b', r'\btesting\b', r'\bspec\b', r'\bmock\b', r'\bfixture\b', r'\bcoverage\b', r'\bassert\b', r'\btestcase\b'],
        "documentation": [r'\bdocs\b', r'\bdoc\b', r'\breadme\b', r'\bcomment\b', r'\bguide\b', r'\btutorial\b', r'\bexample\b', r'\bchangelog\b', r'\busage\b'],
        "infrastructure": [r'\bdocker\b', r'\bci\b', r'\bpipeline\b', r'\bworkflow\b', r'\bjenkins\b', r'\bgithub-actions\b', r'\bbuild\b', r'\bdeployment\b', r'k8s', r'kubernetes', r'\bterraform\b', r'\bhelm\b', r'\benv\b', r'\bdeploy\b', r'\bconfig\b', r'\bconfiguration\b'],
        "dependency": [r'\bupgrade\b', r'\bupdate\b', r'\bbump\b', r'\bdependency\b', r'\bdependencies\b', r'\bpackage\b', r'\bversion\b', r'\bdeps\b', r'\blockfile\b', r'\brequirements\b', r'\byarn\b', r'\bpip\b', r'\bnpm\b'],
        "removal": [r'\bremove\b', r'\bdelete\b', r'\bdrop\b', r'\bdeprecate\b', r'\bobsolete\b', r'\bcleanup unused\b'],
        "security": [r'\bsecurity\b', r'\bvulnerability\b', r'\bsanitize\b', r'\bescape\b', r'\bxss\b', r'\bcsrf\b', r'\bpermission\b', r'\bauthentication\b', r'\bauthorization\b', r'\bauth\b'],
        "chore": [r'\bchore\b', r'\blint\b', r'\bstyle\b', r'\bformat\b', r'\bcode style\b', r'\bcleanup formatting\b']
    }

    # --- Conventional Commit Prefixes ---
    CONVENTIONAL_PREFIXES = {
        "feature": r'^feat(\(.*\))?:',
        "bugfix": r'^fix(\(.*\))?:',
        "documentation": r'^docs(\(.*\))?:',
        "testing": r'^test(\(.*\))?:',
        "performance": r'^perf(\(.*\))?:',
        "refactor": r'^refactor(\(.*\))?:',
        "chore": r'^chore(\(.*\))?:',
        "security": r'^security(\(.*\))?:'
    }

    # --- File Patterns ---
    FILE_PATTERNS = {
        "testing": [r'^test_.*', r'.*\.test\..*', r'.*\.spec\..*', r'^tests/.*'],
        "infrastructure": [r'.*Dockerfile.*', r'.*docker-compose.*', r'.*Jenkinsfile.*', r'^\.github/workflows/.*', r'.*Makefile.*'],
        "documentation": [r'.*README.*', r'^docs/.*']
    }

    # --- Priority Order ---
    PRIORITY = [
        "removal",
        "security",
        "dependency",
        "chore",
        "infrastructure",
        "testing",
        "documentation",
        "performance",
        "refactor",
        "bugfix",
        "feature",
        "other"
    ]

    @classmethod
    def classify_commit(cls, commit: Dict[str, Any]) -> Dict[str, Any]:
        """Classify a commit based on heuristics without AI."""
        message = commit.get("message", "").lower()
        files = commit.get("files", [])
        additions = commit.get("additions", 0)
        deletions = commit.get("deletions", 0)

        signals = {category: 0.0 for category in cls.PRIORITY}

        # 0. Conventional Commit Prefix Signals (+0.4)
        for category, pattern in cls.CONVENTIONAL_PREFIXES.items():
            if re.match(pattern, message):
                signals[category] += 0.4
                break # Only one conventional prefix per message

        # 1. Keyword Signals (+0.4)
        for category, patterns in cls.KEYWORDS.items():
            for pattern in patterns:
                if re.search(pattern, message):
                    signals[category] += 0.4
                    break # Single match per category is enough for keyword signal

        # 2. File Pattern Signals (+0.3)
        for category, patterns in cls.FILE_PATTERNS.items():
            matched = False
            for f in files:
                for pattern in patterns:
                    if re.search(pattern, f):
                        signals[category] += 0.3
                        matched = True
                        break
                if matched:
                    break

        # 3. Diff Statistics & Removal Detection (+0.3)
        # Lower threshold to 1.5 since real removals often have overlapping additions
        # Require at least 10 deletions to avoid flagging tiny cleanups as removals
        is_removal = deletions >= 10 and deletions > (additions * 1.5)
        has_remove_keyword = any(re.search(p, message) for p in cls.KEYWORDS["removal"])
        
        if is_removal and has_remove_keyword:
            signals["removal"] += 0.3
        elif deletions >= 10:
            # High deletions but no keyword, partial signal
            signals["removal"] += 0.15

        # Final Priority Pass (Highest score vs Priority)
        # Collect candidate categories where signal > 0
        candidate_categories = [cat for cat in cls.PRIORITY if signals[cat] > 0]
        
        if candidate_categories:
            # Sort candidates: primarily by score (descending), secondarily by priority index (ascending)
            candidate_categories.sort(
                key=lambda cat: (-signals[cat], cls.PRIORITY.index(cat))
            )
            best_category = candidate_categories[0]
            best_confidence = min(1.0, signals[best_category])
        else:
            best_category = "other"
            best_confidence = 0.1 # Base confidence for other

        return {
            "category": best_category,
            "confidence": round(best_confidence, 2)
        }
            
    @classmethod
    def extract_summary(cls, commit_detail: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a simplified summary of a commit's details."""
        commit_obj = commit_detail.get('commit') or {}
        author_obj = commit_obj.get('author') or {}
        stats = commit_detail.get('stats', {})
        files_list = commit_detail.get('files', [])
        
        message = commit_obj.get('message', '')
        author = author_obj.get('name', 'Unknown')
        date = author_obj.get('date', '')
        
        files_changed = [f.get('filename') for f in files_list] if files_list else []
        additions = stats.get('additions', 0)
        deletions = stats.get('deletions', 0)
        
        # Prepare input for classifier
        classifier_input = {
            "message": message,
            "files": files_changed,
            "additions": additions,
            "deletions": deletions
        }
        
        classification = cls.classify_commit(classifier_input)
        
        # Determine if it's a merge commit (usually more than one parent)
        parents = commit_detail.get('parents', [])
        is_merge = len(parents) > 1
        
        return {
            "sha": commit_detail.get("sha"),
            "message": message,
            "type": classification["category"],
            "classification_confidence": classification["confidence"],
            "author": author,
            "date": date,
            "files": files_list,
            "files_changed": files_changed,
            "additions": additions,
            "deletions": deletions,
            "is_merge": is_merge
        }

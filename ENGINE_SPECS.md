# Git History Storyteller - Engine Specifications

The Statistics Engine employs advanced heuristics to extract meaningful insights from raw GitHub commit metadata. 

## Phase Plan: Advanced Analytics Expansion + Combined Analytics Engine

This phase upgrades the repository analytics pipeline by improving architecture detection, milestone detection, commit classification, and introducing lightweight development phase clustering. The goal is to generate more accurate structural insights before sending signals to the AI narrative generator.

---

## Phase 3 – Advanced Analytics Expansion

### 1. statistics_engine.py
Rewrite `detect_architecture_changes` to use multi-signal validation instead of commit size alone.

Architecture shifts are detected when:
- `commit_size > mean_commit_size + (3 * std_commit_size)`
- `files_changed >= 10`
- `unique_directories_changed >= 3`
- commit message contains refactor keywords (`refactor`, `rewrite`, `restructure`, `migrate`)

`commit_size = additions + deletions`
Directories are extracted from file paths using the top-level folder name.

Return architecture shift objects:
```json
{
  "type": "architecture_shift",
  "commit_sha": "...",
  "date": "...",
  "impact": 1200
}
```

### 2. milestone_detector.py
Add improved milestone detection logic.

`detect_module_introductions`:
- Track top-level directories across commits.
- Trigger milestone when a new directory appears with >=5 files added.

`detect_component_introductions`:
- Detect testing framework introduction using patterns: `test_*`, `*.spec.*`, `*.test.*`, `tests/`
- Detect infrastructure introduction using files: `Dockerfile`, `Jenkinsfile`, `Makefile`, `.github/workflows`, `docker-compose`.

`detect_contributor_growth`:
- Track active contributors per month.
- Trigger milestone when contributors double compared to previous month AND current contributor count >=4.

---

## Phase 4 – Combined Analytics Engine

### 1. Commit Filtering (main.py)
Before analytics processing, filter noisy commits.
Exclude commits where:
- commit message starts with "Merge"
- author login contains "bot" (dependabot, etc.)
- files_changed == 0

### 2. Commit Classification
Update `classify_commit()` to use standardized keyword sets:
- **Feature**: add, implement, feature, feat, introduce
- **Bugfix**: fix, bug, resolve, patch, hotfix
- **Refactor**: refactor, cleanup, rewrite, restructure
- **Performance**: optimize, perf, performance
- **Testing**: test, tests
- **Documentation**: docs, doc
- **Infrastructure**: docker, ci, pipeline, workflow
- **Dependency**: upgrade, update, bump, dependency

### 3. Collaboration Score Update
Update `calculate_collaboration_score()`:
`collaboration_score = unique_authors / sqrt(total_commits)`
Only compute when total_commits >= 10 for the month.

### 4. Development Phase Detection (Lightweight Clustering)
Implement `detect_development_phases()`.
Steps:
1. Group commits by week.
2. Count commits per week.
3. Compute mean weekly commit activity.
4. Mark weeks with commits >= mean as active.
5. Merge consecutive active weeks into development phases.

### Final Analytics Pipeline
```
GitHub API
   |
Commit Filtering
   |
Commit Classification
   |
Statistics Engine
   |
Milestone Detection
   |
Development Phase Clustering
   |
Structured Signals -> Gemini Narrative Generation
```

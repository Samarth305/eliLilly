# Git History Storyteller: Backend Engine Specs (The Middle-Ware)

This document details the deterministic logic, mathematical formulas, and architectural thinking that occurs after the **GitHub API** data fetch and before the **AI Narrative Generation**.

---

## 1. Data Cleaning & Noise Reduction
Before any analysis, the engine filters the raw GitHub response to ensure "Human Signal Only":
- **Merge Filter:** Removes all commits with more than one parent (`is_merge: True`). 
- **Bot/CI Filter:** Excludes authors like `dependabot`, `github-actions`, and `renovate`. Separately filters generic `*bot*` accounts unless the author name is specifically `robot`.
- **Empty Filter:** Removes commits with zero additions/deletions.

---

## 2. Local Heuristic Classification (`CommitAnalyzer`)
**Approach:** Categorize commits without AI using a weighted signal model.

### Probability Signals:
1. **Keyword Signal (+0.4):** Regex matching against 9 categories (feature, bugfix, refactor, performance, testing, docs, infra, dependency, removal).
2. **File Pattern Signal (+0.3):** Regex matching (`re.search`) against 9 categories.
3. **Diff Stat Signal (+0.3):**
   - **Removal Detection:** `deletions >= 10` and `deletions > (additions * 1.5)` combined with keywords like `delete` or `drop`.

**Formula:** 
Confidence Score = $\min(1.0, \sum \text{signals})$

---

## 3. Statistical Modeling (`StatisticsEngine`)

### A. Impact Score
**Formula:**
$$Impact = (Additions + Deletions) + (FilesChanged \times \ln(FilesChanged + 1) \times 10)$$
**Thinking:** The $\ln$ (natural log) normalization prevents a single massive rename or doc update from skewing the project's entire history.

### B. Bus Factor
**Formula:** 
Minimum set of contributors $N$ such that:
$$\sum_{i=1}^{N} Commits_i \geq 0.5 \times TotalCommits$$
**Thinking:** Identifies project risk. If $N=1$, the "Bus Factor" is critical.

### C. Maturity Score
**Formula:** 
$$Maturity = \frac{RefactorCommits + TestCommits}{TotalCommits}$$
**Thinking:** High maturity (>0.3) indicates a project moving out of "rapid prototyping" into "stability and maintenance."

### D. Collaboration Intensity
**Formula:**
$$Intensity = \frac{UniqueAuthors_{month}}{\sqrt{Commits_{month}}}$$
**Thinking:** Square-root scaling of commits prevents high-frequency posters from drowning out team-wide collaborative signals.

### E. Efficiency Index
**Formula:**
$$Efficiency = 100 \times \sqrt{\text{ClampedVelocity}} \times Quality$$
Where:
- **ClampedVelocity:** $\min(Commits_{last\_month} / AvgMonthlyCommits, 2.0)$
- **Quality:** $(Feature + Refactor + Performance) / TotalCommits$
**Thinking:** Square-root scaling and clamping velocity at 2.0 prevents extreme outliers while rewarding consistent high-value output.

### F. Momentum Score
**Formula:**
$$Momentum = \frac{Commits_{last\_30\_days}}{Commits_{previous\_30\_days}}$$
**Thinking:** A real-time "pulse" check. $> 1.0$ indicates the project is accelerating; $< 1.0$ indicates search for stability or a lul in activity.

---

## 4. Development Phase Clustering
**Approach:** Lightweight time-series grouping instead of heavy K-Means.

1. **Aggregation:** Group commits by ISO Week (e.g., `2024-W10`).
2. **Mean Baseline:** Calculate average commits per week across the entire project history.
3. **Activity Detection:** Identify "Active Weeks" (Weeks where $Commits \geq Mean$).
4. **Merging:** Join consecutive Active Weeks into a single **Development Phase**.
5. **Phase Characterization:** For each phase, calculate:
   - **Dominant Type:** Most frequent commit category in that period.
   - **Top Modules:** Top 3 directories affected.
   - **Average Size:** (Additions + Deletions) / Commits.

---

## 5. Milestone Detection (`MilestoneDetector`)
**Thinking:** Correlate disparate signals into a human-readable timeline.

- **Team Growth:** Triggered when the unique contributor count in a month is $> 2\times$ the **3-month moving average**.
- **Structural Shift:** Triggered when an **Architecture Change** is detected (Size > Mean + 2.5σ, touching $\geq 3$ directories).
- **Module Evolution:** Tracks cumulative file additions across commits until a directory hits $\geq 5$ files.
- **Project Launch:** Correlation of the first tag/release with initial high-activity phases.

---

## 6. The Final AI Signal (The Hand-off)
Everything above is bundled into a structured JSON payload:
- **repo_name**
- **bus_factor**
- **development_phases** (with metrics)
- **milestones**
- **architecture_shifts**
- **contributor_insights**

This compressed "**Technical DNA**" is truncated to the **Top 5** occurrences for phases, milestones, and architecture shifts before being sent to **Gemini** or **Ollama**. This allows the AI to write a perfect narrative without having to process thousands of raw lines of code or hitting context limits.

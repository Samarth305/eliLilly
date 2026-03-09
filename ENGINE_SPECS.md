## 1. Contributor Influence Models

### A. Improved Impact Score (Normalized)
The **Impact Score** uses log-normalization to prevent large-scale renames or doc updates from dominating the score.
$$Impact = (Additions + Deletions) + (Files\ Changed \times \log(Files\ Changed + 1) \times 10)$$

*   **Rationale**: Linear scaling on files changed often over-penalizes architectural moves. Logarithmic scaling ensures diminishing returns as the "spread" of a commit increases.
*   **Variable Weights**: A multiplier of 10 on the log-normalized file count balances raw code volume with change complexity.

---

## 2. Team Dynamics & Risk Analytics

### A. Bus Factor Calculation
Measures the repository's resilience to contributor departure.
*   **Definition**: The minimum number of contributors whose combined commits account for **at least 50%** of total commits.
*   **Interpretation**: A Bus Factor of 1 represents a "Single Point of Failure" risk.

### B. Repository Maturity Score
Quantifies the project's focus on stability vs. feature churn.
$$Maturity = \frac{Refactor\ Commits + Test\ Commits}{Total\ Commits}$$
*   **Benchmark**: A score **> 0.30** indicates a mature, production-ready codebase focusing on refinement and stability.

---

## 3. Evolutionary Signals

### A. Adaptive Architecture Change Detection
Identifies significant structural shifts using commit size distribution.
$$Threshold = \mu_{size} + (3 \times \sigma_{size})$$
Where $size = Additions + Deletions$.
*   **Logic**: Instead of a fixed line count, the threshold adaptively moves based on the repository's average commit magnitude. Any commit exceeding 3 standard deviations from the mean is flagged.

### B. Improved Collaboration Score
Measures the distribution of effort month-over-month.
$$Collaboration\ Score = \frac{Unique\ Authors_{month}}{Commits_{month}}$$
*   **Interpretation**: Lower scores indicate centralized work by core maintainers; higher scores indicate a highly distributed community effort.

---

## 4. Categorization Logic
The backend uses a **Keyword-Weighted Classifier** for commit messages:
*   **Feature**: `add`, `implement`, `feature`, `feat`
*   **Bugfix**: `fix`, `bug`, `resolve`, `patch`
*   **Refactor**: `refactor`, `cleanup`
*   **Performance**: `optimize`, `perf`, `performance`
*   **Testing**: `test`, `tests`
*   **Documentation**: `docs`, `doc`

# Git History Storyteller (v3.0)

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=flat&logo=react&logoColor=white)](https://reactjs.org/)
[![GraphQL](https://img.shields.io/badge/GitHub_GraphQL-API-e10098?style=flat&logo=graphql&logoColor=white)](https://docs.github.com/en/graphql)

**Git History Storyteller** is an advanced repository intelligence dashboard that transforms complex Git history into an interactive, AI-driven narrative. It combines high-performance statistical extraction with Large Language Models (LLMs) to tell the unique story of a codebase's evolution.

---

## 🚀 Key Features

### 🧠 Intelligence & Narrative
- **AI-Driven Storytelling**: Generates thematic "Project Evolution" chapters using **Groq (Llama 3.3)** with localized **Ollama** fallback.
- **Project Overviews**: Contextual AI summaries explaining the core intent and current state of the repository.
- **Architectural Shift Detection**: Automatically identifies major refactors or structural pivots based on code impact and commit intent.

### 📊 Advanced Analytics Engine
The core of the system is the **High-Performance Statistics Engine**, which processes thousands of raw Git signals into actionable intelligence:

- **Advanced Hotspots**: Moves beyond raw commit counts to a sophisticated **Risk Score** calculated as `(commit_count * average_impact)`. This highlights complex, frequently changed files that are most likely to contain regressions.
- **Knowledge Silo Detection**: Monitors maintainability risk by calculating the **Contributor Ownership Ratio**. It identifies critical modules where code knowledge is concentrated in a single "silo," posing a significant "Bus Factor" risk.
- **Code Churn & Stability**: Mathematically identifies unstable modules by tracking the ratio of `additions` vs. `deletions` vs. `total_impact`. Files with high churn are flagged as high-maintenance hotspots.
- **Evolutionary Development Phases**: Uses temporal clustering to group commits into logical eras (e.g., "Initial Prototype," "Scaling Refactor," "Stability Period"), allowing for a thematic understanding of project growth.
- **Efficiency Index**: A derivative score of velocity vs. quality, quantifying how effectively specialized categories (Features vs. Refactors) are balanced over time.

### ⚡ Performance & Resilience
- **Persistent SQLite Caching**: Analysis results are cached locally. Returning users experience **<100ms load times** via a dedicated LRU-managed persistence layer.
- **SHA-Based Validation**: The engine automatically checks for new commits on GitHub to ensure the cache never serves stale data.
- **Hybrid Data Fetching**: Optimized GraphQL bulk retrieval combined with REST enrichment for high-fidelity commit data (O(N) complexity).
- **API Stability**: Built-in exponential backoff and retry mechanisms for GitHub API (502/503/504) and rate-limit management.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, SQLite, httpx, Groq SDK.
- **Frontend**: React, Vite, Recharts (Visualizations), Lucide (Icons), Glassmorphism UI.
- **Analysis**: O(N) Complexity engines for linear scalability across thousands of commits.

---

## 🚦 Getting Started

### 1. Prerequisites
- A **GitHub Personal Access Token** (classic or fine-grained).
- A **Groq API Key** (optional but recommended for high-quality narratives).

### 2. Backend Setup
```bash
cd backend
# Create a .env file
echo "GITHUB_TOKEN=your_token" > .env
echo "GROQ_API_KEY=your_key" >> .env

pip install -r requirements.txt
python main.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

---

## 🔄 How it Works

1. **Signal Extraction**: The system pulls down 300+ most recent commits and full repository metadata via GraphQL.
2. **Heuristic Processing**: Every commit is classified into 12 distinct categories (Feature, Bugfix, Refactor, etc.) using file patterns and keyword heuristics.
3. **Statistical Modeling**: The `StatisticsEngine` computes developer velocity, impact scores, and clusters timeline events into logical "Development Phases."
4. **Narrative Synthesis**: Compressed analytical signals are sent to the AI engine to generate a readable project timeline.
5. **Persistence**: Results are stored in an LRU-managed SQLite database for instant retrieval.

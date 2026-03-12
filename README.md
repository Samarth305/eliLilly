# 📖 Git History Storyteller (v3.0)

> **Transforming raw Git signals into meaningful human narratives.**


[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB?style=flat&logo=react&logoColor=white)](https://reactjs.org/)
[![GraphQL](https://img.shields.io/badge/GitHub_GraphQL-API-e10098?style=flat&logo=graphql&logoColor=white)](https://docs.github.com/en/graphql)
[![SQLite](https://img.shields.io/badge/SQLite-Persistence-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

**Git History Storyteller** is an AI-powered repository intelligence dashboard. It goes beyond basic commit tracking to analyze code churn, knowledge distribution, and architectural evolution, translating thousands of technical signals into a compelling, human-readable narrative.

---

## 🚀 Key Features

### 🧠 Intelligence & Narrative Layer
- **AI Story Cards**: Transforms raw technical signals into a structured narrative. Each "Story Card" represents a logical development phase (e.g., "Initial Prototype", "Scaling Pivot", "Stabilization").
- **Project Intelligence Overview**: Real-time AI summaries that explain the core intent and current state of the repository.
- **Architectural Shift Detection**: Automatically identifies major refactors or structural pivots by monitoring high-impact commit clusters.

### 🔍 Advanced Analytics Engine (The "Deep-Dive")
- **Contributor Insights Engine**: 
    - **Core Maintainer Detection**: Identifies individuals responsible for project direction.
    - **Ownership Analysis (Knowledge Silos)**: Detects "high coverage risk" areas where project knowledge is concentrated in too few minds.
    - **High-Impact Scoring**: A weighted metric combining additions, deletions, and file breadth to quantify real developer impact.
- **Hotspot & Churn Analysis**: Uses a sophisticated `Risk = Frequency * Impact` formula to find critical, high-volatility files.
- **Resilience Metrics**: Computes **Bus Factor**, **Maturity Score**, and **Efficiency Index** to quantify the health of the project.

### ⚡ Systems Engineering & Performance
- **Hybrid Data Strategy (v3.0)**: 
    - **GraphQL Bulk Retrieval**: Massive batch fetching of releases, metadata, and 300+ commit headers reduces API roundtrips by 80%.
    - **Parallel REST Enrichment**: 40+ concurrent workers for high-fidelity commit analysis.
- **Persistent SQLite Caching**: Analysis results are persisted locally. Returning users experience **<100ms load times**.
- **Smart Validation**: Automatically checks GitHub for new commits to ensure the cache never serves stale data.
- **API Resilience**: Industrial-grade retry logic with exponential backoff for transient GitHub/AI provider errors.

---

## 🛠️ Tech Stack

### Frontend
- **React + Vite**: High-performance single-page architecture.
- **TailwindCSS**: Premium Glassmorphism UI with custom mesh gradients.
- **Recharts**: Interactive data visualization (Commit Frequency, Hot Modules, Velocity charts).
- **Lucide Icons**: Clean, technical iconography.

### Backend
- **Python FastAPI**: Asynchronous high-throughput API layer.
- **SQLite**: Local persistence and analysis caching.
- **LLM Context Engine**: Optimized prompt engineering for **Groq (Llama 3.3)** and **Google Gemini**, with local **Ollama** fallbacks.
- **GitHub API Gateway**: Hybrid GraphQL and REST implementation.

---

## 🔄 Technical Architecture

```mermaid
graph TD
    UI[React Glassmorphism UI] -->|SSE Stream| API[FastAPI Orchestrator]
    API -->|Validation| Cache[(SQLite Cache)]
    API -->|Bulk Fetch| GH_GQL[GitHub GraphQL API]
    API -->|Enrichment| GH_REST[GitHub REST API]
    API -->|O(N) Processing| SE[Statistics Engine]
    SE -->|Signal Compression| AI[LLM Engine: Groq/Gemini/Ollama]
    AI -->|JSON Artifacts| UI
```

---

## 🚦 Getting Started

### 1. Prerequisites
- Python 3.9+ and Node.js 18+
- GitHub Personal Access Token (classic or fine-grained)
- Groq or Gemini API Key (Optional for AI narratives)

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

---

## 📁 Project Structure
- `backend/`: FastAPI application, O(N) O(N) statistical engines, and AI context services.
- `frontend/`: React dashboard featuring premium UI components and Recharts visualization.
- `README.md`: Comprehensive documentation and project overview.
- `repository_cache.db`: SQLite persistence layer (auto-generated).

---

## 🎯 Project Vision
To empower developers and tech leads with "Repository X-Ray Vision," reducing code audit times from days to seconds by finding the signal in the noise of thousands of commits.

# Git History Storyteller

An AI-powered repository analysis dashboard that transforms complex Git history into a structured narrative.

## 📖 Project Overview
*   **Purpose:** To help developers and managers quickly understand the lifecycle, health, and evolution of any given software project.
*   **Mechanism:** Extracts raw signals from Git history, processes them through a statistical engine, and uses AI to write a creative, human-readable timeline mapping out the repository's journey.

## ⚙️ Key Functionalities
*   **Metadata Extraction:** Recursively fetches commits, contributors, pull requests, and structural data using GitHub's GraphQL and REST APIs.
*   **Heuristic Analysis:** Analyzes commit messages, diff sizes, and file extensions to categorize commits (e.g., feature, bugfix, refactor, dependency).
*   **Evolutionary Storytelling:** Leverages Groq (Llama 3 70b) or local Ollama models to generate creative, thematic chapter summaries of development phases.
*   **Health Metrics Calculation:** Computes Bus Factor (team resilience), Maturity Score, Codebase Efficiency, and top Contributors' Impact automatically.
*   **"Hot Module" Detection:** Tracks the specific folders and files that are most frequently mutated over time.

## 🔄 Data Flow Architecture
1. **User Input:** User submits a valid GitHub repository URL via the React frontend.
2. **Data Orchestration (Backend):** FastAPI receives the request and triggers the `GitHubService`.
3. **Signal Gathering:** Backend pulls down hundreds of recent commits and repository metrics.
4. **Statistical Processing:** The `StatisticsEngine` organizes commits chronologically, groups them into defined "Development Phases," identifies "Architecture Shifts," and calculates Risk/Maturity scores.
5. **AI Generation:** The highly compressed `structured_signals` object is injected into a specialized prompt and sent to Groq. 
6. **Response Synthesis:** Groq streams back a JSON array of creative "Story Cards" representing the project's timeline.
7. **Visualization:** The completed dataset is sent back to the frontend, rendering the interactive Glassmorphism UI, Recharts graphics, and Markdown narratives.

---

## ✨ Recent Enhancements (v2.0)

*   **Primary LLM Migration:** Upgraded from Gemini to Groq (`llama-3.3-70b-versatile`) as the primary AI engine, with Ollama (`gemma3:4b`) configured as a local fallback.
*   **Creative Story Chapters:** AI prompts strictly enforce creative, thematic chapter titles instead of generic development phases.
*   **Deep Narrative Context:** Narrative generation now analyzes Milestones, Architecture Changes, and Contributor Insights in addition to commit phases.
*   **Optimized Data Fetching:** Implemented GraphQL for bulk fetching of GitHub repository data, drastically improving analysis speed over traditional REST.
*   **Premium UI & Aesthetics:**
    *   Dark, animated "mesh gradient" backgrounds.
    *   Refined **Glassmorphism** for data cards (`backdrop-filter: blur(16px)`).
    *   Hover glow micro-interactions across timelines, cards, and charts.
    *   Improved typography scale, tracking, and font selections (`Outfit`, `Inter`, `Fira Code`).
*   **Enhanced Visualizations:** Replaced the legacy "Development Velocity" line chart with an interactive "Commit Frequency" Bar Chart mapping monthly activity.
*   **Robust Data Models:** Fixed critical API bugs where `bus_factor` and `maturity_score` were being stripped from the Pydantic API response.
*   **Full Dockerization:** 
    *   Project is fully containerized using `docker-compose`.
    *   Frontend served via NGINX.
    *   Backend backend dependencies (like `groq`) correctly mapped in `requirements.txt`.
*   **Clean Version Control:** Sanitized `.gitignore` to automatically exclude all local `debug_*.py` development scripts.

---

## 🛠️ Tech Stack

*   **Frontend:** React, Vite, TailwindCSS (Typography plugin), Lucide Icons, Recharts.
*   **Backend:** Python FastAPI, Uvicorn, httpx, Pydantic, Groq API SDK.
*   **Data Source:** GitHub GraphQL & REST API.

---

## 🚦 Getting Started (Local Development)

### Backend Setup
1. `cd backend`
2. Create `.env`:
   ```env
   GITHUB_TOKEN=your_github_token
   GROQ_API_KEY=your_groq_api_key
   ```
3. `pip install -r requirements.txt`
4. `python main.py`

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npm run dev`

---

## 🐳 Getting Started (Docker)

Ensure your `.env` is set up inside the `backend` directory, then simply run:

```bash
docker-compose up --build -d
```

*   Frontend will be available at `http://localhost:5173`
*   Backend API will be running on `http://localhost:8000`

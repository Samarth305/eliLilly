# Git History Storyteller

Git History Storyteller is an AI-powered repository analysis dashboard that transforms complex Git history into a compelling, structured narrative. It leverages statistical analysis and Large Language Models (Gemini) to explain how a project evolved, identify key contributors, and visualize team dynamics.

## 🚀 Recent Features (v2.0)

Since the latest push, the following core features and enhancements have been implemented:

### 1. Contributor Insights Engine
- **Core Maintainer Detection**: Automatically identifies developers responsible for >= 20% of the project's commit volume.
- **High Impact Statistics**: Calculates a weighted impact score for every contributor based on files changed, additions, and deletions per commit.
- **Code Ownership Tracking**: Intelligent module attribution that identifies which contributors "own" specific parts of the codebase.
- **Collaboration Intensity**: Tracks the unique number of active contributors month-by-month to measure team growth and collaboration spikes.

### 2. Scaled Historical Analysis
- **Increased Depth**: The analysis limit has been doubled to **200 detailed commits**, providing a much deeper historical perspective.
- **Optimized Fetching**: Backend now reads up to **500 raw commits** to extract the most meaningful signals.

### 3. Enriched Repository Metrics
New metrics have been added to the main dashboard header for a 360-degree project overview:
- **Pull Requests**: Total count of all open and closed PRs.
- **Forks**: Total number of repository forks.
- **Stars**: Real-time GitHub star count.

### 4. Advanced Visualizations
- **Contribution Patterns**: A new **Line Chart** (powered by Recharts) visualizes the repo's activity pulse over time.
- **Hot Modules**: Bar charts identifying the most frequently modified directories.
- **Interactive Timeline**: A vertical timeline mapping releases and major architecture shifts.

### 5. AI Story Cards
- The long-form AI narrative has been refactored into **Story Cards**.
- Each card represents a logical development phase (e.g., "Initial Setup", "Feature Burst", "Stabilization").
- Specialized logic for **Team Dynamics Narratives**, where the AI explains how specific contributors shaped the project.

---

## 🛠️ Tech Stack

- **Frontend**: React, Vite, TailwindCSS (Typography plugin), Lucide Icons, Recharts.
- **Backend**: Python FastAPI, Uvicorn, httpx, Pydantic.
- **AI**: Google Gemini API (gemini-2.0-flash).
- **Data Source**: GitHub REST API.

---

## 🚦 Getting Started

### Backend Setup
1. Navigate to `/backend`.
2. Create a `.env` file with:
   ```env
   GITHUB_TOKEN=your_github_token
   GEMINI_API_KEY=your_gemini_api_key
   ```
3. Install dependencies: `pip install -r requirements.txt`.
4. Run: `python main.py`.

### Frontend Setup
1. Navigate to `/frontend`.
2. Install dependencies: `npm install`.
3. Run: `npm run dev`.

---

## 📁 Project Structure

- `backend/`: FastAPI application, commit analysis logic, and Gemini service integration.
- `frontend/`: React dashboard with Recharts visualization and premium UI components.
- `.gitignore`: Configured to exclude Python venvs, node_modules, and environment files.

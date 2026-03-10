import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
import httpx
import asyncio

from utils import parse_github_url
from github_service import GitHubService
from commit_analyzer import CommitAnalyzer
from statistics_engine import StatisticsEngine
from milestone_detector import MilestoneDetector
from gemini_service import GeminiService
from contributor_analyzer import ContributorAnalyzer

load_dotenv()

app = FastAPI(title="Git History Storyteller API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    repo_url: str

class AnalysisResponse(BaseModel):
    repository_stats: dict
    development_phases: list
    milestones: list
    contributors: list
    activity_bursts: list
    hot_modules: list
    architecture_changes: list
    contributor_insights: dict
    story: list
    efficiency_index: dict
    commit_distribution: list
    momentum: float

@app.post("/analyze-repository", response_model=AnalysisResponse)
async def analyze_repository(request: AnalyzeRequest):
    try:
        owner, repo = parse_github_url(request.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    github_service = GitHubService()
    gemini_service = GeminiService()
    
    try:
        # 1. Fetch data
        repo_info = await github_service.get_repository_info(owner, repo)
        # Ensure we try to read all commits
        raw_commits = await github_service.get_commits(owner, repo, per_page=100)
        branches = await github_service.get_branches(owner, repo)
        contributors = await github_service.get_contributors(owner, repo)
        releases = await github_service.get_releases(owner, repo)
        pull_requests = await github_service.get_pull_requests(owner, repo)
        
        # 2. Extract commit details in batches (200 at a time)
        detailed_commits = []
        sem = asyncio.Semaphore(50)
        
        async def fetch_commit(sha: str):
            async with sem:
                detail = await github_service.get_commit_details(owner, repo, sha)
                if detail:
                    return CommitAnalyzer.extract_summary(detail)
                return None

        # Process in batches of 200 to reduce memory overhead
        batch_size = 200
        for i in range(0, len(raw_commits), batch_size):
            batch = raw_commits[i : i + batch_size]
            tasks = [asyncio.create_task(fetch_commit(rc.get("sha"))) for rc in batch if rc.get("sha")]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in results:
                if res and not isinstance(res, Exception):
                    detailed_commits.append(res)

                    
        # 3. Filter commits for noise reduction
        filtered_commits = []
        bot_keywords = ["dependabot", "github-actions", "renovate", "sync-bot"]
        for c in detailed_commits:
            author = c.get("author", "").lower()
            files_changed = len(c.get("files_changed", []))
            
            # Exclude merging (using is_merge flag), bot accounts, and 0-file changes
            if c.get("is_merge"):
                continue
            if any(bot in author for bot in bot_keywords):
                continue
            if "bot" in author and author != "robot":
                continue
            if files_changed == 0:
                continue
            
            filtered_commits.append(c)
            
        if not filtered_commits:
            raise HTTPException(status_code=400, detail="No valid commits found for analysis")
            
        # 4. Statistical Analysis
        frequencies = StatisticsEngine.compute_commit_frequency(filtered_commits)
        bursts = StatisticsEngine.detect_bursts(frequencies.get("commits_per_week", {}))
        inactivity = StatisticsEngine.detect_inactivity(filtered_commits)
        dominance = StatisticsEngine.get_contributor_dominance(filtered_commits)
        hot_modules = StatisticsEngine.detect_hot_modules(filtered_commits)
        arch_changes = StatisticsEngine.detect_architecture_changes(filtered_commits)
        commit_distribution = StatisticsEngine.calculate_commit_distribution(filtered_commits)
        
        # 5. Contributor Analysis
        contributor_insights = ContributorAnalyzer.analyze(filtered_commits)
        
        # 6. Milestone Detection
        milestones = MilestoneDetector.generate_milestones(filtered_commits, releases)
        
        # 7. Advanced Analytics
        bus_factor = StatisticsEngine.calculate_bus_factor(filtered_commits)
        maturity_score = StatisticsEngine.calculate_maturity_score(filtered_commits)
        collaboration_intensity = StatisticsEngine.calculate_collaboration_score(filtered_commits)
        development_phases = StatisticsEngine.detect_development_phases(filtered_commits)
        efficiency_index = StatisticsEngine.calculate_efficiency_index(filtered_commits)
        momentum = StatisticsEngine.calculate_momentum(filtered_commits)
        
        # Structure data for Gemini
        gemini_signals = {
            "repository_name": repo_info.get("full_name"),
            "description": repo_info.get("description"),
            "total_commits_analyzed": len(detailed_commits),
            "commit_frequencies": frequencies,
            "activity_bursts": bursts,
            "inactivity_periods": inactivity,
            "architecture_changes": arch_changes,
            "contributor_dominance": dominance,
            "contributor_insights": contributor_insights,
            "milestones": milestones,
            "hot_modules": hot_modules,
            "bus_factor": bus_factor,
            "maturity_score": maturity_score,
            "collaboration_intensity": collaboration_intensity,
            "repo_name": repo,
            "development_phases": development_phases,
            "efficiency_index": efficiency_index,
            "commit_distribution": commit_distribution
        }
        
        # 5. Connect to Gemini for story analysis
        story = await gemini_service.generate_story(gemini_signals)
        
        # Build Response
        # We synthesize 'development_phases' as Gemini discusses them, or as dummy array if we want strictly parsed.
        # But we will pass it out to frontend as an array or extract it.
        # For simplicity in prototype, we'll keep empty lists for typed structures if not easily parsed and rely on the UI rendering the story.
        
        response = {
            "repository_stats": {
                "total_analyzed_commits": len(raw_commits),
                "total_contributors_count": len(contributors),
                "branches_count": len(branches),
                "releases_count": len(releases),
                "pull_requests_count": len(pull_requests),
                "forks_count": repo_info.get("forks_count", 0),
                "stars": repo_info.get("stargazers_count", 0),
            },
            "development_phases": development_phases,
            "milestones": milestones,
            "contributors": [
                {
                    "name": c.get("login"),
                    "contributions": c.get("contributions")
                }
                for c in contributors
            ],
            "activity_bursts": bursts,
            "hot_modules": hot_modules,
            "architecture_changes": arch_changes,
            "contributor_insights": contributor_insights,
            "bus_factor": bus_factor,
            "maturity_score": maturity_score,
            "story": story,
            "efficiency_index": efficiency_index,
            "commit_distribution": commit_distribution,
            "momentum": momentum
        }
        
        return response
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"GitHub API error: {e.response.text}")
    finally:
        await github_service.close()

if __name__ == "__main__":
    # Start the server using uvicorn e.g. python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

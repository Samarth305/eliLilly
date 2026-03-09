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
    story: list

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
        raw_commits = await github_service.get_commits(owner, repo, per_page=100, max_pages=3)
        branches = await github_service.get_branches(owner, repo)
        contributors = await github_service.get_contributors(owner, repo)
        releases = await github_service.get_releases(owner, repo)
        
        # 2. Extract commit details concurrently (limit to 100 to avoid rate limit/slowdown)
        detailed_commits = []
        
        async def fetch_commit(sha: str):
            detail = await github_service.get_commit_details(owner, repo, sha)
            if detail:
                return CommitAnalyzer.extract_summary(detail)
            return None

        # Gather promises
        tasks = [asyncio.create_task(fetch_commit(rc.get("sha"))) for rc in raw_commits[:100] if rc.get("sha")]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if res and not isinstance(res, Exception):
                detailed_commits.append(res)

                    
        # 3. Statistical Analysis
        frequencies = StatisticsEngine.compute_commit_frequency(detailed_commits)
        bursts = StatisticsEngine.detect_bursts(frequencies.get("commits_per_week", {}))
        inactivity = StatisticsEngine.detect_inactivity(detailed_commits)
        dominance = StatisticsEngine.get_contributor_dominance(detailed_commits)
        hot_modules = StatisticsEngine.detect_hot_modules(detailed_commits)
        arch_changes = StatisticsEngine.detect_architecture_changes(detailed_commits, threshold=200)
        
        # 4. Milestone Detection
        milestones = MilestoneDetector.generate_milestones(detailed_commits, releases)
        
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
            "contributor_impact": StatisticsEngine.analyze_contributor_impact(detailed_commits),
            "code_ownership": StatisticsEngine.analyze_code_ownership(detailed_commits),
            "collaboration_intensity": StatisticsEngine.calculate_collaboration_intensity(detailed_commits),
            "milestones": milestones,
            "hot_modules": hot_modules
        }
        
        # 5. Connect to Gemini for story analysis
        story = gemini_service.generate_story(gemini_signals)
        
        # Build Response
        # We synthesize 'development_phases' as Gemini discusses them, or as dummy array if we want strictly parsed.
        # But we will pass it out to frontend as an array or extract it.
        # For simplicity in prototype, we'll keep empty lists for typed structures if not easily parsed and rely on the UI rendering the story.
        
        response = {
            "repository_stats": {
                "total_analyzed_commits": len(detailed_commits),
                "total_contributors_count": len(contributors),
                "branches_count": len(branches),
                "releases_count": len(releases),
                "stars": repo_info.get("stargazers_count", 0),
            },
            "development_phases": [],  # Could be extracted by regex from Gemini story if needed
            "milestones": milestones,
            "contributors": [c.get("login") for c in contributors[:10]],
            "activity_bursts": bursts,
            "hot_modules": [{"module": k, "count": v} for k, v in hot_modules.items()],
            "architecture_changes": arch_changes,
            "contributor_insights": gemini_signals["contributor_impact"],
            "story": story
        }
        
        return response
        
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"GitHub API error: {e.response.text}")
    finally:
        await github_service.close()

if __name__ == "__main__":
    # Start the server using uvicorn e.g. python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
from groq_service import GroqService
from contributor_analyzer import ContributorAnalyzer
from cache_service import CacheService

load_dotenv()

app = FastAPI(title="Git History Storyteller API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProgressManager:
    def __init__(self):
        self.queues = {}

    def get_queue(self, request_id: str):
        if request_id not in self.queues:
            self.queues[request_id] = asyncio.Queue()
        return self.queues[request_id]

    async def push(self, request_id: str, message: str):
        if request_id in self.queues:
            await self.queues[request_id].put(message)

    def remove_queue(self, request_id: str):
        if request_id in self.queues:
            del self.queues[request_id]

progress_manager = ProgressManager()

# Global Service Instantiation
github_service = GitHubService()
story_service = GroqService()
cache_service = CacheService(db_path=os.getenv("DB_PATH", "repository_cache.db"))

@app.get("/analyze-stream")
async def analyze_stream(request_id: str = Query(...)):
    async def event_generator():
        queue = progress_manager.get_queue(request_id)
        try:
            while True:
                message = await queue.get()
                if message == "DONE":
                    break
                yield f"data: {message}\n\n"
        finally:
            progress_manager.remove_queue(request_id)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.delete("/clear-cache")
async def clear_cache(repo_url: str = Query(...)):
    """Clear cache for a specific repository."""
    try:
        cache_service.invalidate_cache(repo_url)
        return {"message": f"Cache cleared for {repo_url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear-all-cache")
async def clear_all_cache():
    """Clear the entire repository cache."""
    try:
        cache_service.clear_all_cache()
        return {"message": "Entire cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AnalyzeRequest(BaseModel):
    repo_url: str
    request_id: str = None
    bypass_cache: bool = False

class AnalysisResponse(BaseModel):
    repository_stats: dict
    development_phases: list
    milestones: list
    contributors: list
    activity_bursts: list
    hot_modules: list
    architecture_changes: list
    contributor_insights: dict
    repo_overview: str
    commit_frequencies: dict
    story: list
    efficiency_index: dict
    commit_distribution: list
    momentum: float
    bus_factor: int
    maturity_score: float

@app.post("/analyze-repository", response_model=AnalysisResponse)
async def analyze_repository(request: AnalyzeRequest):
    request_id = request.request_id
    
    async def update_progress(msg: str):
        if request_id:
            await progress_manager.push(request_id, msg)

    try:
        owner, repo = parse_github_url(request.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 0. Check Cache
    if not request.bypass_cache:
        cached_result = cache_service.get_cached_analysis(request.repo_url)
        if cached_result:
            await update_progress("Checking for repository updates...")
            # Validate if it's still fresh by checking latest commit SHA
            try:
                # Fetch only the very latest commit SHA via GraphQL
                latest_sha_data = await github_service.fetch_commits_paginated_graphql(owner, repo, limit=1)
                if latest_sha_data:
                    current_sha = latest_sha_data[0].get("oid")
                    if current_sha == cached_result["latest_commit_sha"]:
                        await update_progress("Using cached analysis...")
                        await update_progress("DONE")
                        return cached_result["analysis_data"]
            except Exception as e:
                print(f"Cache validation failed: {e}")
                # If validation fails for some reason (network, etc), we just proceed to full re-analysis
    
    try:
        await update_progress("Fetching repository metadata...")
        # 1. Fetch bulk data via GraphQL (Massive efficiency gain)
        gql_data = await github_service.fetch_repository_data_graphql(owner, repo)
        repo_data = gql_data.get("repository")
        if not repo_data:
            raise HTTPException(status_code=404, detail="Repository not found")
            
        repo_info = {
            "full_name": repo_data.get("fullName"),
            "description": repo_data.get("description"),
            "stargazers_count": repo_data.get("stargazerCount", 0),
            "forks_count": repo_data.get("forkCount", 0),
        }
        
        pull_requests_count = repo_data.get("pullRequests", {}).get("totalCount", 0)
        releases_data = repo_data.get("releases", {})
        releases_count = releases_data.get("totalCount", 0)
        releases_nodes = releases_data.get("nodes", [])
        
        await update_progress("Downloading commit history...")
        # 2. Paginated GraphQL for large history (Now up to 10,000)
        raw_commits = await github_service.fetch_commits_paginated_graphql(owner, repo, limit=10000)
        total_commits_count = len(raw_commits)
        
        await update_progress(f"Processing patterns for {total_commits_count} commits...")
        
        # 3. Smart Hybrid Enrichment
        # First, pre-process ALL commits for statistics (lightweight)
        all_processed_commits = []
        for c in raw_commits:
            author_data = c.get("author") or {}
            user_data = author_data.get("user") or {}
            
            author_name = user_data.get("login") or author_data.get("name") or "Unknown"
            message = c.get("message", "")
            
            classification = CommitAnalyzer.classify_commit({
                "message": message, 
                "files": [], 
                "additions": c.get("additions", 0), 
                "deletions": c.get("deletions", 0)
            })
            
            all_processed_commits.append({
                "sha": c.get("oid"),
                "message": message,
                "date": c.get("committedDate"),
                "author": author_name,
                "type": classification["category"],
                "classification_confidence": classification["confidence"],
                "additions": c.get("additions", 0),
                "deletions": c.get("deletions", 0),
                "files_changed": [], # Empty for base processed
                "is_merge": c.get("parents", {}).get("totalCount", 0) > 1
            })

        # Now sample for DEEP enrichment (Story & Evolution)
        sampled_raw = StatisticsEngine.sample_commits(raw_commits, target_total=500)
        await update_progress(f"Performing deep analysis on {len(sampled_raw)} key events...")
        
        detailed_commits = []
        sem = asyncio.Semaphore(40)
        
        # Calculate size threshold for outlier detection in history
        import statistics
        sizes = [c.get("additions", 0) + c.get("deletions", 0) for c in sampled_raw]
        threshold = statistics.mean(sizes) + 2.5 * statistics.stdev(sizes) if len(sizes) > 1 else 1000
        
        async def enrich_commit(gql_commit: dict):
            sha = gql_commit.get("oid")
            size = gql_commit.get("additions", 0) + gql_commit.get("deletions", 0)
            
            # Enrich if: it's sampled (we force enrichment for the 500)
            async with sem:
                detail = await github_service.get_commit_details(owner, repo, sha)
                if detail:
                    return CommitAnalyzer.extract_summary(detail)
            
            # This should rarely happen now that we only gather sampled ones
            return None
        
        # Execute enrichment tasks for sampled commits
        tasks = [asyncio.create_task(enrich_commit(c)) for c in sampled_raw]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for res in results:
            if res and not isinstance(res, Exception):
                detailed_commits.append(res)

        # 1.5 Fetch README and generate overview
        readme_content = await github_service.get_readme(owner, repo)
        repo_overview = await story_service.generate_overview(repo, readme_content)

        # Still need contributors and branches via REST
        contributors = await github_service.get_contributors(owner, repo)
        branches = await github_service.get_branches(owner, repo)

        # 4. Filter ALL commits for statistical accuracy
        all_filtered_commits = []
        bot_keywords = ["dependabot", "github-actions", "renovate", "sync-bot"]
        for c in all_processed_commits:
            author = c.get("author", "").lower()
            if c.get("is_merge"): continue
            if any(bot in author for bot in bot_keywords): continue
            if "bot" in author and author != "robot": continue
            all_filtered_commits.append(c)
            
        if not all_filtered_commits:
            raise HTTPException(status_code=400, detail="No valid commits found for analysis")
            
        await update_progress("Computing repository metrics...")
            
        # 5. Statistical Analysis (on full 10k dataset)
        frequencies = StatisticsEngine.compute_commit_frequency(all_filtered_commits)
        bursts = StatisticsEngine.detect_bursts(frequencies.get("commits_per_week", {}))
        inactivity = StatisticsEngine.detect_inactivity(all_filtered_commits)
        dominance = StatisticsEngine.get_contributor_dominance(all_filtered_commits)
        hot_modules = StatisticsEngine.detect_hot_modules(all_filtered_commits)
        arch_changes = StatisticsEngine.detect_architecture_changes(all_filtered_commits)
        commit_distribution = StatisticsEngine.calculate_commit_distribution(all_filtered_commits)
        
        # 6. Contributor Analysis
        contributor_insights = ContributorAnalyzer.analyze(all_filtered_commits)
        
        # 7. Milestone Detection (on sampled detailed commits)
        milestones = MilestoneDetector.generate_milestones(detailed_commits, releases_nodes)
        
        await update_progress("Detecting development phases...")
        
        # 8. Advanced Analytics (on full dataset)
        bus_factor = StatisticsEngine.calculate_bus_factor(all_filtered_commits)
        maturity_score = StatisticsEngine.calculate_maturity_score(all_filtered_commits)
        collaboration_intensity = StatisticsEngine.calculate_collaboration_score(all_filtered_commits)
        development_phases = StatisticsEngine.detect_development_phases(all_filtered_commits)
        efficiency_index = StatisticsEngine.calculate_efficiency_index(all_filtered_commits)
        momentum = StatisticsEngine.calculate_momentum(all_filtered_commits)
        
        await update_progress("Identifying architecture shifts...")
        
        # Structure data for the AI Narrative Engine
        story_signals = {
            "repository_name": repo_info.get("full_name"),
            "description": repo_info.get("description"),
            "total_commits_analyzed": len(all_processed_commits),
            "sampled_commits_for_narrative": len(detailed_commits),
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
        
        # 5. Connect to Groq for story analysis (with Ollama fallback)
        await update_progress("Generating AI narrative...")
        story = await story_service.generate_story(story_signals)
        
        await update_progress("DONE")
        
        # Build Response
        # We synthesize 'development_phases' as Gemini discusses them, or as dummy array if we want strictly parsed.
        # But we will pass it out to frontend as an array or extract it.
        # For simplicity in prototype, we'll keep empty lists for typed structures if not easily parsed and rely on the UI rendering the story.
        
        response = {
            "repository_stats": {
                "total_analyzed_commits": total_commits_count,
                "total_contributors_count": len(contributors),
                "branches_count": len(branches),
                "releases_count": releases_count,
                "pull_requests_count": pull_requests_count,
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
            "repo_overview": repo_overview,
            "commit_frequencies": frequencies,
            "story": story,
            "efficiency_index": efficiency_index,
            "commit_distribution": commit_distribution,
            "momentum": momentum
        }
        
        # 8. Save to Cache
        try:
            # We need the SHA of the latest commit used in this analysis
            latest_commit_sha = raw_commits[0].get("oid") if raw_commits else None
            cache_service.save_analysis(request.repo_url, latest_commit_sha, response)
        except Exception as e:
            print(f"Error saving to cache: {e}")
            
        return response
        
    except httpx.HTTPStatusError as e:
        import traceback
        traceback.print_exc()
        # Instead of propagating 502, return a 503 so the user knows it's an upstream issue we can't solve now
        status_code = e.response.status_code
        if status_code >= 500:
             raise HTTPException(status_code=503, detail="GitHub is currently experiencing issues. Please try again in 30 seconds.")
        raise HTTPException(status_code=status_code, detail=f"GitHub API error: {e.response.text}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        pass

if __name__ == "__main__":
    # Start the server using uvicorn e.g. python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

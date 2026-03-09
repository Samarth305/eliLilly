import asyncio
from github_service import GitHubService
from statistics_engine import StatisticsEngine
from commit_analyzer import CommitAnalyzer

async def test_analytics():
    gh = GitHubService()
    owner, repo = "keploy", "blog-website"
    
    # 1. Fetch commits
    commits = await gh.get_commits(owner, repo, per_page=100)
    print(f"Raw Commits: {len(commits)}")
    
    # 2. Extract and Filter
    detailed_commits = []
    
    sem = asyncio.Semaphore(20)
    async def fetch_commit(sha: str):
        async with sem:
            detail = await gh.get_commit_details(owner, repo, sha)
            if detail:
                return CommitAnalyzer.extract_summary(detail)
            return None

    tasks = [asyncio.create_task(fetch_commit(c.get("sha"))) for c in commits[:50] if c.get("sha")]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for res in results:
        if res and not isinstance(res, Exception):
            message = res.get("message", "").lower()
            author = res.get("author", "").lower()
            files_changed = len(res.get("files", []))
            
            if not message.startswith("merge") and "bot" not in author and files_changed > 0:
                detailed_commits.append(res)
                
    print(f"\nFiltered Commits (sample size): {len(detailed_commits)}")
    
    if len(detailed_commits) == 0:
        print("No valid commits found in sample.")
        await gh.close()
        return

    # 3. Test New Rules
    phases = StatisticsEngine.detect_development_phases(detailed_commits)
    arch = StatisticsEngine.detect_architecture_changes(detailed_commits)
    bus = StatisticsEngine.calculate_bus_factor(detailed_commits)
    mat = StatisticsEngine.calculate_maturity_score(detailed_commits)
    collab = StatisticsEngine.calculate_collaboration_score(detailed_commits)
    
    print("\n--- Development Phases ---")
    for p in phases:
        print(p)
        
    print("\n--- Architecture Shifts ---")
    for a in arch:
        print(a)
        
    print(f"\nBus Factor: {bus}")
    print(f"Maturity Score: {mat}")
    
    print("\n--- Collaboration Intensity ---")
    print(collab)
    
    await gh.close()

if __name__ == "__main__":
    asyncio.run(test_analytics())

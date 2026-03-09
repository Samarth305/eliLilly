import asyncio
import os
from dotenv import load_dotenv
from github_service import GitHubService
from commit_analyzer import CommitAnalyzer

load_dotenv()

async def test_classification():
    gh = GitHubService()
    owner, repo = "keploy", "blog-website"
    
    # Fetch partial commits
    commits = await gh.get_commits(owner, repo, per_page=20)
    print(f"Raw Commits Fetched: {len(commits)}")
    
    sem = asyncio.Semaphore(10)
    async def fetch_commit(sha: str):
        async with sem:
            detail = await gh.get_commit_details(owner, repo, sha)
            if detail:
                return CommitAnalyzer.extract_summary(detail)
            return None

    tasks = [asyncio.create_task(fetch_commit(c.get("sha"))) for c in commits[:10] if c.get("sha")]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for res in results:
        if res and not isinstance(res, Exception):
            print(f"\nMessage: {res['message'][:50]}...")
            print(f"Additions: {res['additions']} | Deletions: {res['deletions']} | Files: {len(res['files_changed'])}")
            print(f"--> Type: {res['type']} (Confidence: {res['classification_confidence']})")
                
    await gh.close()

if __name__ == "__main__":
    asyncio.run(test_classification())

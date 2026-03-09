import asyncio
import os
from dotenv import load_dotenv
from github_service import GitHubService

load_dotenv()

async def test_pagination():
    gh = GitHubService()
    owner, repo = "keploy", "blog-website"
    
    # Try fetching contributors with anon=1
    url_contribs = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    anon_contribs = await gh._fetch_all_pages(url_contribs, params={"anon": "true", "per_page": 100})
    print(f"Contributors (anon=true): {len(anon_contribs)}")
    
    # Fetch PRs and group by state
    prs = await gh.get_pull_requests(owner, repo)
    states = {}
    for pr in prs:
        state = pr.get("state")
        states[state] = states.get(state, 0) + 1
    
    print(f"Total PRs fetched: {len(prs)}")
    print(f"PR States: {states}")
    
    await gh.close()

if __name__ == "__main__":
    asyncio.run(test_pagination())

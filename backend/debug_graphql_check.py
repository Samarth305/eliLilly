import asyncio
import os
from dotenv import load_dotenv
from github_service import GitHubService

load_dotenv()

async def verify_graphql():
    service = GitHubService()
    owner = "pallets"
    repo = "click"
    
    print(f"--- Diagnosing GraphQL for {owner}/{repo} ---")
    try:
        data = await service.fetch_repository_data_graphql(owner, repo, commit_limit=5)
        repository = data.get("repository")
        if repository:
            print("✅ GraphQL Success!")
            print(f"Repo Name: {repository.get('fullName')}")
            print(f"Description: {repository.get('description')[:50]}...")
            
            history = repository.get("defaultBranchRef", {}).get("target", {}).get("history", {})
            commits = history.get("nodes", [])
            print(f"Fetched {len(commits)} commits via GraphQL.")
            
            if commits:
                first = commits[0]
                print(f"Last Commit: {first.get('message')[:30]}...")
                print(f"Stats: +{first.get('additions')} / -{first.get('deletions')} (Detected via GraphQL)")
        else:
            print("❌ GraphQL returned empty data for repository node.")
    except Exception as e:
        print(f"❌ GraphQL Error: {e}")
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(verify_graphql())

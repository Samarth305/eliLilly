import httpx
import os
import asyncio
import time
from typing import Dict, Any, List

GITHUB_API_URL = "https://api.github.com"

class GitHubService:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        self.token = token.strip("'\"") if token else None
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Git-History-Storyteller"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        
        # Connection pooling and rate limit synchronization
        limits = httpx.Limits(max_connections=50)
        self.client = httpx.AsyncClient(headers=self.headers, timeout=60.0, limits=limits)
        self._rate_limit_reset = 0
        self._rate_limit_lock = asyncio.Lock()
        self.graphql_url = "https://api.github.com/graphql"

    async def _execute_graphql(self, query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generic GraphQL execution with rate-limit guarding."""
        await self._wait_if_rate_limited()
        payload = {"query": query, "variables": variables or {}}
        response = await self.client.post(self.graphql_url, json=payload)
        
        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                reset = int(response.headers["X-RateLimit-Reset"])
                self._rate_limit_reset = max(self._rate_limit_reset, reset)
                await self._wait_if_rate_limited()
                return await self._execute_graphql(query, variables)
        
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise Exception(f"GraphQL Errors: {data['errors']}")
        return data.get("data", {})

    async def fetch_repository_data_graphql(self, owner: str, repo: str, commit_limit: int = 100) -> Dict[str, Any]:
        """Fetch repo metadata, PRs, releases, and initial commit history in one go."""
        query = """
        query($owner: String!, $repo: String!, $limit: Int!) {
          repository(owner: $owner, name: $repo) {
            name
            fullName: nameWithOwner
            description
            stargazerCount
            forkCount
            languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node { name }
              }
            }
            defaultBranchRef {
              name
              target {
                ... on Commit {
                  history(first: $limit) {
                    totalCount
                    pageInfo {
                      hasNextPage
                      endCursor
                    }
                    nodes {
                      oid
                      message
                      committedDate
                      additions
                      deletions
                      changedFiles
                      author {
                        name
                        user { login }
                      }
                      parents { totalCount }
                    }
                  }
                }
              }
            }
            pullRequests(first: 100, states: [OPEN, CLOSED, MERGED]) {
              totalCount
              nodes {
                title
                state
                createdAt
                mergedAt
              }
            }
            releases(first: 50, orderBy: {field: CREATED_AT, direction: DESC}) {
              totalCount
              nodes {
                tagName
                name
                publishedAt
                createdAt
              }
            }
          }
        }
        """
        variables = {"owner": owner, "repo": repo, "limit": commit_limit}
        return await self._execute_graphql(query, variables)

    async def _wait_if_rate_limited(self):
        """Shared guard to prevent multiple parallel tasks from hitting 403 or sleeping redundantly."""
        now = time.time()
        if now < self._rate_limit_reset:
            async with self._rate_limit_lock:
                # Re-check after acquiring lock
                wait_duration = self._rate_limit_reset - time.time()
                if wait_duration > 0:
                    print(f"Global Rate Limit Active. Centralized wait for {int(wait_duration)}s...")
                    await asyncio.sleep(wait_duration)

    async def _fetch_all_pages(self, url: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generic pagination method that fetches pages until GitHub returns an empty list
        or a list smaller than per_page (indicating the last page).
        """
        if params is None:
            params = {}
        if "per_page" not in params:
            params["per_page"] = 100
            
        results = []
        page = 1
        
        while True:
            await self._wait_if_rate_limited()
            params["page"] = page
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                if response.status_code == 403:
                    remaining = response.headers.get("X-RateLimit-Remaining")
                    if remaining == "0":
                        reset = int(response.headers["X-RateLimit-Reset"])
                        self._rate_limit_reset = max(self._rate_limit_reset, reset)
                        await self._wait_if_rate_limited()
                        continue # Retry
                    print(f"Rate limit reached ({response.status_code}) for {url}. Remaining: {remaining}")
                else:
                    print(f"API Error ({response.status_code}) on {url}: {response.text}")
                break
                
            page_data = response.json()
            if not page_data:
                break
                
            results.extend(page_data)
            
            # If we received less than per_page, we've hit the end
            if len(page_data) < params["per_page"]:
                break
                
            if page >= 500 or len(results) > 50000: 
                print(f"Reached failsafe limit for {url}")
                break
                
            page += 1
            
            # Rate limit protection: Sleep 0.2s every 5 pages
            if page % 5 == 0:
                await asyncio.sleep(0.2)
            
        return results

    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_commits(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"
        return await self._fetch_all_pages(url, params={"per_page": per_page})
        
    async def get_commit_details(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        await self._wait_if_rate_limited()
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits/{sha}"
        response = await self.client.get(url)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining == "0":
                reset = int(response.headers["X-RateLimit-Reset"])
                self._rate_limit_reset = max(self._rate_limit_reset, reset)
                await self._wait_if_rate_limited()
                return await self.get_commit_details(owner, repo, sha) # Retry
            print(f"Rate limit reached for details ({sha}). Remaining: {remaining}")
        return {}

    async def get_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches"
        return await self._fetch_all_pages(url)

    async def get_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contributors"
        return await self._fetch_all_pages(url)

    async def get_releases(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/releases"
        return await self._fetch_all_pages(url)

    async def get_pull_requests(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Fetch pull requests (open and closed)."""
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/pulls"
        return await self._fetch_all_pages(url, params={"state": "all"})
    
    async def get_readme(self, owner: str, repo: str) -> str:
        """Fetch the README content of a repository."""
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/readme"
        try:
            response = await self.client.get(url, headers={"Accept": "application/vnd.github.v3.raw"})
            if response.status_code == 200:
                return response.text
            return ""
        except Exception as e:
            print(f"Error fetching README: {e}")
            return ""
    
    async def close(self):
        await self.client.aclose()

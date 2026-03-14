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
        self.client = httpx.AsyncClient(headers=self.headers, timeout=60.0, limits=limits, follow_redirects=True)
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

    async def fetch_repository_data_graphql(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repo metadata, PRs, and releases."""
        query = """
        query($owner: String!, $repo: String!) {
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
        variables = {"owner": owner, "repo": repo}
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.post(self.graphql_url, json={"query": query, "variables": variables})
                if response.status_code == 200:
                    return response.json().get("data", {})
                elif response.status_code in [502, 503, 504]:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt+1))
                        continue
                print(f"GraphQL Meta Error ({response.status_code}): {response.text}")
                break
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                break
        return {}

    async def fetch_commits_paginated_graphql(self, owner: str, repo: str, limit: int = 10000) -> List[Dict[str, Any]]:
        """Fetch commit history efficiently via GraphQL with retries."""
        query = """
        query($owner: String!, $repo: String!, $cursor: String, $pageSize: Int!) {
          repository(owner: $owner, name: $repo) {
            defaultBranchRef {
              target {
                ... on Commit {
                  history(first: $pageSize, after: $cursor) {
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
          }
        }
        """
        
        commits = []
        cursor = None
        page_size = min(limit, 100)
        
        while len(commits) < limit:
            variables = {"owner": owner, "repo": repo, "cursor": cursor, "pageSize": page_size}
            
            max_retries = 3
            success = False
            for attempt in range(max_retries):
                try:
                    response = await self.client.post(self.graphql_url, json={"query": query, "variables": variables})
                    if response.status_code == 200:
                        success = True
                        break
                    elif response.status_code in [502, 503, 504]:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1 * (attempt + 1))
                            continue
                    print(f"GraphQL Commit Error ({response.status_code}): {response.text}")
                    break
                except (httpx.RequestError, httpx.TimeoutException):
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    break
            
            if not success:
                break
                
            data = response.json().get("data", {})
            repo_data = data.get("repository")
            if not repo_data or not repo_data.get("defaultBranchRef"):
                break
                
            history = repo_data["defaultBranchRef"]["target"]["history"]
            new_nodes = history.get("nodes", [])
            commits.extend(new_nodes)
            
            page_info = history.get("pageInfo", {})
            if not page_info.get("hasNextPage") or len(commits) >= limit:
                break
            cursor = page_info.get("endCursor")
            
        return commits[:limit]

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
        Included retries for 502/503/504.
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
            
            # Implementation of retries for transient server errors
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await self.client.get(url, params=params)
                    if response.status_code == 200:
                        break
                    elif response.status_code in [502, 503, 504]:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(1 * (attempt + 1))
                            continue
                    
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
                except httpx.RequestError as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    raise e
            else:
                # All retries failed
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
        """Fetch full commit details with retry logic."""
        await self._wait_if_rate_limited()
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits/{sha}"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.get(url)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code in [502, 503, 504]:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                elif response.status_code == 403:
                    remaining = response.headers.get("X-RateLimit-Remaining")
                    if remaining == "0":
                        reset = int(response.headers["X-RateLimit-Reset"])
                        self._rate_limit_reset = max(self._rate_limit_reset, reset)
                        await self._wait_if_rate_limited()
                        return await self.get_commit_details(owner, repo, sha) # Recursive retry
                    print(f"Rate limit reached for details ({sha}). Remaining: {remaining}")
                
                break # Non-retryable error or success (though 200 returned early)
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                break
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
        """Fetch the repository README content with retries."""
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/readme"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.get(url, headers={"Accept": "application/vnd.github.raw"})
                if response.status_code == 200:
                    return response.text
                elif response.status_code in [502, 503, 504]:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                break
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
                break
        return ""
    
    async def close(self):
        await self.client.aclose()

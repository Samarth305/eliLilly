import httpx
import os
import asyncio
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
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

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
            params["page"] = page
            response = await self.client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"API Error ({response.status_code}) on {url}: {response.text}")
                break
                
            page_data = response.json()
            if not page_data:
                break
                
            results.extend(page_data)
            
            # If we received less than per_page, we've hit the end
            if len(page_data) < params["per_page"]:
                break
                
            # Failsafe limit just in case to prevent infinite loops (e.g., 50,000 items)
            if page >= 500: 
                print(f"Reached failsafe limit of 500 pages for {url}")
                break
                
            page += 1
            
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
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits/{sha}"
        response = await self.client.get(url)
        if response.status_code == 200:
            return response.json()
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
    
    async def close(self):
        await self.client.aclose()

import httpx
import os
import asyncio
from typing import Dict, Any, List

GITHUB_API_URL = "https://api.github.com"

class GitHubService:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Git-History-Storyteller"
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0)

    async def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_commits(self, owner: str, repo: str, per_page: int = 100, max_pages: int = 3) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"
        commits = []
        for page in range(1, max_pages + 1):
            response = await self.client.get(url, params={"per_page": per_page, "page": page})
            if response.status_code != 200:
                break
            page_data = response.json()
            if not page_data:
                break
            commits.extend(page_data)
        return commits
        
    async def get_commit_details(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits/{sha}"
        response = await self.client.get(url)
        if response.status_code == 200:
            return response.json()
        return {}

    async def get_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/branches"
        response = await self.client.get(url, params={"per_page": 100})
        if response.status_code == 200:
            return response.json()
        return []

    async def get_contributors(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contributors"
        response = await self.client.get(url, params={"per_page": 100})
        if response.status_code == 200:
            return response.json()
        return []

    async def get_releases(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/releases"
        response = await self.client.get(url, params={"per_page": 100})
        if response.status_code == 200:
            return response.json()
        return []
    
    async def close(self):
        await self.client.aclose()

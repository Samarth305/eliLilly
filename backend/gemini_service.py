import os
import json
import httpx
import asyncio
import google.generativeai as genai
from typing import Dict, Any, List

class GeminiService:
    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("Warning: GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=gemini_api_key)
        # Using gemini-2.0-flash since we need structured generation
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    async def generate_story(self, structured_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        prompt = self._build_prompt(structured_signals)
        
        try:
            # Try Gemini first (Async)
            response = await self.model.generate_content_async(prompt)
            text = response.text.strip()
            return self._parse_json_story(text)
        except Exception as e:
            print(f"Gemini API failed or quota exceeded: {e}. Falling back to Ollama...")
            # Fallback to local Ollama with specialized prompt
            return await self.generate_story_with_ollama(structured_signals)

    async def generate_story_with_ollama(self, structured_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback to local Ollama API (gemma3:4b)."""
        prompt = self._build_ollama_prompt(structured_signals)
        
        # Try host.docker.internal (for Docker) and localhost (for native)
        urls = [
            "http://host.docker.internal:11434/api/generate",
            "http://localhost:11434/api/generate"
        ]
        
        payload = {
            "model": "gemma3:4b",
            "prompt": prompt,
            "stream": False
        }
        
        last_exception = None
        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    raw_text = data.get("response", "").strip()
                    
                    # Attempt to parse as JSON first
                    try:
                        return self._parse_json_story(raw_text)
                    except:
                        # Wrap pure text into story cards
                        return [{
                            "title": "Evolution Narrative (Ollama)",
                            "period": "Analysis Period",
                            "description": raw_text
                        }]
            except Exception as e:
                last_exception = e
                continue
        
        print(f"Ollama fallback failed on all URLs. Last error: {last_exception}")
        return [{
            "title": "Analysis Unavailable",
            "period": "All AI Services Failed",
            "description": f"Both Gemini and local Ollama were unavailable. (Error: {last_exception})"
        }]

    def _build_ollama_prompt(self, structured_signals: Dict[str, Any]) -> str:
        repo_name = structured_signals.get("repo_name", "Unknown Repository")
        bus_factor = structured_signals.get("bus_factor", "Unknown")
        development_phases = json.dumps(structured_signals.get("development_phases", []), indent=2)
        milestones = json.dumps(structured_signals.get("milestones", []), indent=2)
        architecture_shifts = json.dumps(structured_signals.get("architecture_changes", []), indent=2)
        contributors = json.dumps(structured_signals.get("contributor_insights", {}), indent=2)

        return f"""
You are an expert software engineering historian analyzing the evolution of a Git repository.

Your task is to interpret repository analytics and explain how the project evolved over time.

You will receive structured repository signals including development phases, milestones, architecture changes, and contributor statistics.

Use these signals to produce a clear and technical narrative describing the lifecycle of the project.

Focus on:
• how development activity changed over time
• major feature development phases
• architectural refactoring or restructuring
• contributor growth or collaboration patterns
• infrastructure or tooling changes
• overall maturity of the repository

The explanation must remain chronological and technically clear.
Keep the explanation concise but insightful.

---

Repository Analytics:

Repository Name:
{repo_name}

Bus Factor:
{bus_factor}

Development Phases:
{development_phases}

Milestones:
{milestones}

Architecture Changes:
{architecture_shifts}

Contributor Insights:
{contributors}

---

Instructions:
1. Describe the **early stage of the repository** and its initial development.
2. Explain **major growth phases** where commit activity increased.
3. Highlight **significant architecture changes or refactors**.
4. Explain **team collaboration patterns** and contributor growth.
5. Summarize the **current maturity and stability of the project**.

---

Output Requirements:
Write the response as a short technical narrative (4–8 sentences).
Do not include bullet points or markdown formatting.
Do not invent information that is not present in the repository signals.
The goal is to explain the evolution of the repository in a human-readable way.
"""

    def _build_prompt(self, structured_signals: Dict[str, Any]) -> str:
        return f"""
        You are analyzing the evolution of a software repository.
        
        You will receive structured development phases extracted from Git history.
        
        Each phase contains:
        - start
        - end
        - commit_count
        - dominant_commit_type
        - top_modules
        - contributors
        - avg_commit_size
        
        Your task is to interpret each phase and explain what likely happened during that period.
        
        Focus on:
        - development activity
        - architectural changes
        - feature expansion
        - bug fixing cycles
        - collaboration patterns
        - module evolution
        
        Write a concise narrative for each phase.
        
        Return JSON in this exact format:
        {{
          "story_cards": [
            {{
              "title": "Phase title",
              "period": "start → end",
              "description": "clear explanation of what happened in the repository during this phase"
            }}
          ]
        }}
        
        Data to analyze:
        {json.dumps(structured_signals.get('development_phases', []), indent=2, default=str)}
        """

    def _parse_json_story(self, text: str) -> List[Dict[str, Any]]:
        # Remove any markdown code block wrap (e.g. ```json ... ```)
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text[:-3]
            
        text = text.strip()
        
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            # If not JSON, return as is (let the caller wrap it)
            raise ValueError("Not valid JSON")

        if isinstance(parsed, dict) and "story_cards" in parsed:
            return parsed["story_cards"]
        if isinstance(parsed, list):
            return parsed
        return parsed

import os
import json
import httpx
import asyncio
from groq import AsyncGroq
from typing import Dict, Any, List

class GroqService:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("Warning: GROQ_API_KEY not found in environment")
        else:
            # Diagnostic: Print the prefix to confirm which project is being used
            print(f"GroqService initialized with key prefix: {self.api_key[:10]}...")
            
        self.client = AsyncGroq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
        
    async def generate_story(self, structured_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Compress signals aggressively (Top 5)
        structured_signals["development_phases"] = structured_signals.get("development_phases", [])[:5]
        structured_signals["milestones"] = structured_signals.get("milestones", [])[:5]
        structured_signals["architecture_changes"] = structured_signals.get("architecture_changes", [])[:5]
        
        prompt = self._build_prompt(structured_signals)
        print("\n" + "="*50)
        print(f"🚀 [GROQ] Sending Prompt ({len(prompt)} chars):")
        print(prompt[:500] + "...\n[TRUNCATED IN LOGS]")
        print("="*50 + "\n")
        
        try:
            # Using Groq Chat Completions API
            response = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a software engineering historian. Always return strict, valid JSON matching the exact schema requested without any markdown blocks or conversational text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                response_format={"type": "json_object"},
                temperature=0.3
            )
            text = response.choices[0].message.content.strip()
            print("✅ [GROQ] Story generated successfully.")
            return self._parse_json_story(text, source="Groq")
        except Exception as e:
            print(f"Groq API failed: {e}")
            print("Falling back to Ollama...")
            return await self.generate_story_with_ollama(structured_signals)

    async def generate_overview(self, repo_name: str, readme_content: str) -> str:
        """Generate a concise, high-level overview of the repository based on its README."""
        if not readme_content or len(readme_content) < 50:
            return "No comprehensive README found to generate deep repository overview."

        # Limit README content to avoid token overflow
        truncated_readme = readme_content[:4000]
        
        prompt = f"""
        Analyze the following README content for the repository: {repo_name}
        Provide a concise, 2-3 sentence high-level overview of what this project does, its core value proposition, and primary tech stack.
        Return ONLY the plain text overview. No markdown formatting.
        
        README Content:
        {truncated_readme}
        """
        
        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a technical documentarian. Provide a concise repository overview."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating overview: {e}")
            return "Unable to generate AI overview at this time."

    async def generate_story_with_ollama(self, structured_signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback to local Ollama API (gemma3:4b)."""
        prompt = self._build_ollama_prompt(structured_signals)
        
        print("\n" + "="*50)
        print(f"🦙 [OLLAMA] Sending Prompt ({len(prompt)} chars):")
        print(prompt[:500] + "...\n[TRUNCATED IN LOGS]")
        print("="*50 + "\n")
        
        urls = [
            "http://host.docker.internal:11434/api/generate",
            "http://localhost:11434/api/generate"
        ]
        
        payload = {
            "model": "gemma3:4b",
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "num_predict": 600,
                "temperature": 0.3,
                "top_k": 40,
                "top_p": 0.9
            }
        }
        
        last_exception = None
        for url in urls:
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    response = await client.post(url, json=payload)
                    response.raise_for_status()
                    data = response.json()
                    raw_text = data.get("response", "").strip()
                    
                    try:
                        print("✅ [OLLAMA] Story generated successfully.")
                        return self._parse_json_story(raw_text, source="Ollama")
                    except:
                        print("⚠️ [OLLAMA] Failed to parse JSON, returning raw text.")
                        return [{
                            "title": "Evolution Narrative (Ollama)",
                            "period": "Analysis Period",
                            "description": raw_text
                        }]
            except Exception as e:
                last_exception = e
                continue
        
        return [{
            "title": "Analysis Unavailable",
            "period": "All AI Services Failed",
            "description": f"Both Gemini and local Ollama were unavailable. (Error: {last_exception})"
        }]

    def _build_ollama_prompt(self, structured_signals: Dict[str, Any]) -> str:
        repo_name = structured_signals.get("repo_name", "Unknown Repository")
        bus_factor = structured_signals.get("bus_factor", "Unknown")
        
        dev_phases_data = structured_signals.get("development_phases", [])[:5]
        milestones_data = structured_signals.get("milestones", [])[:5]
        arch_changes_data = structured_signals.get("architecture_changes", [])[:5]
        
        development_phases = json.dumps(dev_phases_data, indent=2)
        milestones = json.dumps(milestones_data, indent=2)
        architecture_shifts = json.dumps(arch_changes_data, indent=2)
        contributors = json.dumps(structured_signals.get("contributor_insights", {}), indent=2)

        return f"""
You are an expert software engineering historian.
Analyze the evolution of this repository and return a JSON object containing an array of story cards.
You must return only valid JSON and nothing else.

Data:
Repo: {repo_name}
Bus Factor: {bus_factor}
Phases: {development_phases}
Milestones: {milestones}
Architecture: {architecture_shifts}
Contributors: {contributors}

Return EXACTLY this JSON format:
{{
  "story_cards": [
    {{
      "title": "Creative, thematic chapter title (e.g., The Genesis Commit)",
      "period": "Overall Analysis",
      "description": "Write a clear technical narrative (4-8 sentences) explaining the project's evolution, major growth, and architecture shifts."
    }}
  ]
}}
"""

    def _build_prompt(self, structured_signals: Dict[str, Any]) -> str:
        repo_name = structured_signals.get("repository_name", "Unknown Repository")
        dev_phases_data = structured_signals.get("development_phases", [])
        milestones_data = structured_signals.get("milestones", [])
        arch_changes_data = structured_signals.get("architecture_changes", [])
        contributors_data = structured_signals.get("contributor_insights", {})

        return f"""
        You are analyzing the evolution of a software repository named: {repo_name}
        
        You will receive structured signals extracted from Git history:
        1. Development Phases
        2. Milestones
        3. Architecture Changes
        4. Contributor Insights
        
        Your task is to interpret this data and explain what likely happened during the repository's evolution.
        
        Focus on:
        - development activity
        - architectural changes
        - feature expansion
        - bug fixing cycles
        - collaboration patterns
        - module evolution
        
        Write a concise, engaging narrative for each phase or major event.
        CRITICAL: Make the "title" highly creative, thematic, and specific to the actual technical work done (e.g., "The Database Awakening", "Birth of the Automation Pipeline", "The Great Refactoring". Do NOT use generic names like "Active Development Phase 1").
        
        Return JSON in this exact format:
        {{
          "story_cards": [
            {{
              "title": "Creative, thematic chapter title",
              "period": "start → end or specific date",
              "description": "clear explanation of what happened in the repository during this time"
            }}
          ]
        }}
        
        Data to analyze:
        --- Development Phases ---
        {json.dumps(dev_phases_data, indent=2, default=str)}
        
        --- Milestones ---
        {json.dumps(milestones_data, indent=2, default=str)}
        
        --- Architecture Changes ---
        {json.dumps(arch_changes_data, indent=2, default=str)}
        
        --- Contributors ---
        {json.dumps(contributors_data, indent=2, default=str)}
        """

    def _parse_json_story(self, text: str, source: str = "Unknown") -> List[Dict[str, Any]]:
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        try:
            parsed = json.loads(text)
        except:
            raise ValueError("Not valid JSON")

        story_cards = []
        if isinstance(parsed, dict) and "story_cards" in parsed:
            story_cards = parsed["story_cards"]
        elif isinstance(parsed, list):
            story_cards = parsed
        else:
            story_cards = [{"title": "Evolution Summary", "period": "Analysis Period", "description": text}]
            
        # Tag the first card with the AI source so the user knows exactly who wrote it
        if story_cards and isinstance(story_cards[0], dict):
             original_desc = story_cards[0].get("description", "")
             story_cards[0]["description"] = f"[Generated by {source}] {original_desc}"
             
        return story_cards

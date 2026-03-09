import os
import json
import google.generativeai as genai
from typing import Dict, Any

class GeminiService:
    def __init__(self):
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            print("Warning: GEMINI_API_KEY not found in environment")
        
        genai.configure(api_key=gemini_api_key)
        # Using gemini-2.0-flash since we need structured generation
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
    def generate_story(self, structured_signals: Dict[str, Any]) -> str:
        prompt = f"""
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
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Remove any markdown code block wrap (e.g. ```json ... ```)
            if text.startswith("```json"):
                text = text.replace("```json", "", 1)
            if text.endswith("```"):
                text = text[:-3]
                
            text = text.strip()
            
            # Robust extraction of the story_cards array
            parsed = json.loads(text)
            if "story_cards" in parsed:
                return parsed["story_cards"]
            
            return parsed
            
            # Fallback if regex fails but text might be raw JSON
            return json.loads(text)
        except Exception as e:
            return [{"title": "Error generating story", "content": f"JSON Parse Error: {str(e)}"}]

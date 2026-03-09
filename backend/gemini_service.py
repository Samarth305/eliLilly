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
        # Using gemini-2.5-flash since we need structured generation
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    def generate_story(self, structured_signals: Dict[str, Any]) -> str:
        prompt = f"""
        You are an expert software engineer and technical project historian.
        I will provide you with structured statistical data and key metadata about a GitHub repository's evolution.
        
        Your task is to generate a comprehensive, structured narrative describing how this project evolved over time, 
        its major development phases, architectural changes, bursts of activity, and periods of inactivity.
        
        Analyze the following structured signals:
        {json.dumps(structured_signals, indent=2, default=str)}
        
        Focus on interpreting:
        - The development phases (e.g., initial development, feature expansion, stabilization).
        - Highlights of architectural shifts based on the 'architecture_changes' listed.
        - Meaningful bursts of activity or lack thereof.
        - Team dynamics and contributor impact using the 'contributor_insights' data.
        
        CRITICAL INSTRUCTION:
        Do NOT output raw markdown text. You must output a valid JSON array of "Story Cards". 
        Each object in the array should represent a logical section or phase of the story.
        
        Analyze and explain the team dynamics using the 'contributor_insights' signal:
        - Identify Core Maintainers (those with significant commit ratios) and their impact.
        - Highlight High Impact Contributors and how they shaped the codebase.
        - Discuss Code Ownership (which authors were leading specific modules).
        - Mention Collaboration Intensity and patterns over time.
        
        Each card must follow this JSON structure: {{"title": "Card Title", "content": "Markdown content"}}.
        Include at least one card specifically explaining the team dynamics and contributor impact.
        Do not just list the JSON keys; weave them into a narrative (e.g., "Alice emerged as the primary guardian of the auth module...").
        
        Example Output Format:
        [
          {{
            "title": "The Team Dynamics",
            "content": "The project was primarily shaped by..."
          }}
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Robust extraction of the JSON array using regex
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                json_str = match.group(0)
                return json.loads(json_str)
            
            # Fallback if regex fails but text might be raw JSON
            return json.loads(text)
        except Exception as e:
            return [{"title": "Error generating story", "content": f"JSON Parse Error: {str(e)}"}]

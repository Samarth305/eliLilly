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
        
        CRITICAL INSTRUCTION:
        Do NOT output raw markdown text. You must output a valid JSON array of "Story Cards". 
        Each object in the array should represent a logical section or phase of the story.
        Do NOT include contributor statistics or individuals in these story cards, keep it strictly to the project's evolution, phases, and architecture.
        
        Example Output Format:
        [
          {{
            "title": "Initial Inception & Setup",
            "content": "The repository began as a small module..."
          }},
          {{
            "title": "Feature Expansion Phase",
            "content": "Between June 2021 and August 2021, activity spiked..."
          }}
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            # Try to strip markdown JSON formatting if Gemini wraps it
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            return json.loads(text.strip())
        except Exception as e:
            return [{"title": "Error generating story", "content": str(e)}]

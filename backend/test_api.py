import httpx
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                "http://localhost:8000/analyze-repository",
                json={"repo_url": "https://github.com/pallets/click"}
            )
            print("Status:", resp.status_code)
            if resp.status_code == 200:
                data = resp.json()
                print("Keys received:", list(data.keys()))
                print("Total analyzed commits:", data.get("repository_stats", {}).get("total_analyzed_commits"))
                print("Bus Factor:", data.get("bus_factor"))
                print("Efficiency Index:", data.get("efficiency_index", {}).get("score"))
                print("Momentum Score:", data.get("momentum"))
                
                phases = data.get("development_phases", [])
                print(f"Development Phases Detected: {len(phases)}")
                for i, p in enumerate(phases[:3]):
                    print(f"  [{i+1}] {p.get('start')} -> {p.get('end')} ({p.get('dominant_commit_type')})")
                
                print("Story Cards:", len(data.get("story", [])))
                with open("test_response.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("Response saved to test_response.json")
            else:
                print("Error Details:", resp.text)
    except Exception as e:
        print(f"Connection Error: {e}")

asyncio.run(main())

import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def diagnose_429():
    api_key = os.getenv("GEMINI_API_KEY")
    print("="*60)
    print(f"🔍 DEEP DIAGNOSIS FOR KEY: {api_key[:10]}...{api_key[-4:] if api_key else ''}")
    print("="*60)
    
    if not api_key:
        print("❌ NO API KEY FOUND IN .env")
        return

    # Use raw REST API to bypass SDK obfuscation
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts":[{"text": "Hello, this is a tiny test."}]}]
    }

    try:
        async with httpx.AsyncClient() as client:
            print("⏳ Sending raw HTTP request to Google API...")
            response = await client.post(url, json=payload)
            
            print(f"\n📡 HTTP Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! The key works perfectly right now.")
                return

            # If it's a 429, we dissect the exact reason from Google's raw JSON
            error_data = response.json().get("error", {})
            print(f"❌ EXACT GOOGLE ERROR TRACE:")
            print(f"Code: {error_data.get('code')}")
            print(f"Message: {error_data.get('message')}")
            print(f"Status: {error_data.get('status')}")
            
            if response.status_code == 429:
                print("\n🚨 WHY YOU ARE GETTING 'TOO MANY REQUESTS':")
                msg = error_data.get("message", "").lower()
                
                if "quota" in msg and ("day" in msg or "daily" in msg):
                    print("➡️ DIAGNOSIS: DAILY TOTAL HIT")
                    print("Google's Free Tier only allows 1,500 requests per day per project.")
                    print("Even if the key is new, the PROJECT it belongs to has hit its 24-hour limit.")
                elif "quota" in msg and ("minute" in msg or "rpm" in msg):
                    print("➡️ DIAGNOSIS: PER-MINUTE SPAM LIMIT")
                    print("Google's Free Tier only allows 15 requests per minute.")
                    print("Are you clicking 'Analyze' multiple times fast, or is a browser loop firing POST requests continuously?")
                elif "resource" in msg:
                    print("➡️ DIAGNOSIS: REGIONAL CLOUD EXHAUSTION (Google's Fault)")
                    print("Google's servers in your global region are currently overloaded for free-tier users.")
                else:
                    print("➡️ DIAGNOSIS: UNKNOWN 429. Look at the exact message above.")
            
    except Exception as e:
        print(f"\n❌ Network or Parsing Failure: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_429())

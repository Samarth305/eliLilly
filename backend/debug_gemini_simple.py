import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

async def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: No GEMINI_API_KEY found in .env")
        return

    print("="*50)
    print(f"🔑 Using Key Prefix: {api_key[:10]}...")
    print("="*50)

    try:
        # Configure SDK
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        print("⏳ Sending request to Gemini: 'Say hi.'")
        
        # Make the simplest possible call
        response = await model.generate_content_async("Say hi.")
        
        print("\n✅ SUCCESS!")
        print(f"🤖 Gemini replied: {response.text}")
        
    except Exception as e:
        print("\n❌ FAILED!")
        print(f"Error Details: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())

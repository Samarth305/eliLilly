import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def debug_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"--- Diagnosing Gemini Key: {api_key[:8]}...{api_key[-4:]} ---")
    
    if not api_key or "YOUR_" in api_key:
        print("❌ Error: No valid API key found in .env")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        print("Sending test heartbeat to Gemini...")
        response = model.generate_content("Say 'Gemini is Active' in one word.")
        print(f"✅ Success! Response: {response.text.strip()}")
        
    except Exception as e:
        print("❌ Gemini API Error Detected!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        
        error_str = str(e).lower()
        if "429" in error_str:
            if "quota" in error_str:
                if "day" in error_str or "daily" in error_str:
                    print("\n🚨 DIAGNOSIS: DAILY QUOTA EXHAUSTED")
                    print("This means the TOTAL limit for the day (24h) is hit for this PROJECT.")
                elif "minute" in error_str or "rpm" in error_str:
                    print("\n🚨 DIAGNOSIS: RATE LIMIT (RPM) HIT")
                    print("You are sending requests too fast. Wait 60 seconds.")
            else:
                print("\n🚨 DIAGNOSIS: Resource Exhausted (Generic 429)")
        elif "403" in error_str:
            print("\n🚨 DIAGNOSIS: PERMISSION DENIED")
            print("The key might be invalid, or the Gemini API is not enabled for this project.")
        elif "400" in error_str:
            print("\n🚨 DIAGNOSIS: BAD REQUEST")
            print("Check if the model name 'gemini-2.0-flash' is correct for your region.")

if __name__ == "__main__":
    debug_gemini()

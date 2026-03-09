import asyncio
from main import analyze_repository, AnalyzeRequest

async def test():
    req = AnalyzeRequest(repo_url="https://github.com/pallets/click")
    try:
        res = await analyze_repository(req)
        print("Success!")
        print(res)
    except Exception as e:
        print(f"Error caught: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

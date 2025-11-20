"""
Example script showing how to use the Astrological Insight API
"""
import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_api():
    """Test the API endpoints"""
    
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("Testing Astrological Insight API with Cohere")
        print("=" * 60 + "\n")
        
        # 1. Health Check
        print("1. Health Check")
        print("-" * 60)
        response = await client.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
        
        # 2. Root Endpoint
        print("2. API Information")
        print("-" * 60)
        response = await client.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
        
        # 3. Generate Insight (English)
        print("3. Generate Insight (English)")
        print("-" * 60)
        payload = {
            "name": "Alice",
            "birth_date": "1995-07-23",
            "user_id": "user_alice_123"
        }
        response = await client.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Zodiac: {result.get('zodiac')}")
        print(f"Insight: {result.get('insight')}")
        print(f"Cache Hit: {result.get('cache_hit')}")
        print(f"Language: {result.get('language')}\n")
        
        # 4. Generate Insight (Hindi) - will use translation
        print("4. Generate Insight (Hindi)")
        print("-" * 60)
        payload = {
            "name": "Bob",
            "birth_date": "1990-03-21",
            "user_id": "user_bob_456"
        }
        response = await client.post(f"{BASE_URL}/predict?language=hi", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Zodiac: {result.get('zodiac')}")
        print(f"Insight: {result.get('insight')}")
        print(f"Cache Hit: {result.get('cache_hit')}")
        print(f"Language: {result.get('language')}\n")
        
        # 5. Cache Stats
        print("5. Cache Statistics")
        print("-" * 60)
        response = await client.get(f"{BASE_URL}/cache/stats")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}\n")
        
        # 6. Test Cache Hit (request same as #3)
        print("6. Test Cache Hit (same request as #3)")
        print("-" * 60)
        payload = {
            "name": "Alice",
            "birth_date": "1995-07-23",
            "user_id": "user_alice_123"
        }
        response = await client.post(f"{BASE_URL}/predict", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Zodiac: {result.get('zodiac')}")
        print(f"Insight: {result.get('insight')}")
        print(f"Cache Hit: {result.get('cache_hit')} (should be True)")
        print(f"User Score: {result.get('user_score')}\n")
        
        print("=" * 60)
        print("All API tests completed!")
        print("=" * 60)

if __name__ == "__main__":
    print("\nMake sure the server is running:")
    print("  uvicorn app.main:app --reload\n")
    
    try:
        asyncio.run(test_api())
    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to the API.")
        print("Please start the server first:")
        print("  cd /Users/razzzeeev/astro")
        print("  source venv/bin/activate")
        print("  uvicorn app.main:app --reload\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


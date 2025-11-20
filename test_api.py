import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.cache import cache_service

client = TestClient(app)

def test_read_main():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data
    assert data["version"] == "2.0.0"

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data

def test_predict_insight():
    """Test basic insight prediction"""
    payload = {
        "name": "Ritika",
        "birth_date": "1995-08-20",
        "birth_time": "14:30",
        "birth_place": "Jaipur, India"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["zodiac"] == "Leo"
    assert "insight" in data
    assert data["language"] == "en"
    assert isinstance(data["cache_hit"], bool)

def test_predict_insight_with_user_id():
    """Test insight prediction with user ID for personalization"""
    payload = {
        "name": "Ritika",
        "birth_date": "1995-08-20",
        "birth_time": "14:30",
        "birth_place": "Jaipur, India",
        "user_id": "test_user_123"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["zodiac"] == "Leo"
    assert "insight" in data
    # User score should be present if user_id provided
    assert "user_score" in data

def test_predict_insight_with_language():
    """Test insight prediction with Hindi language"""
    payload = {
        "name": "Ritika",
        "birth_date": "1995-08-20",
        "birth_time": "14:30",
        "birth_place": "Jaipur, India"
    }
    response = client.post("/predict?language=hi", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "hi"
    assert "insight" in data

def test_predict_insight_with_coordinates():
    """Test insight prediction with latitude/longitude for Panchang"""
    payload = {
        "name": "Ritika",
        "birth_date": "1995-08-20",
        "birth_time": "14:30",
        "birth_place": "Jaipur, India",
        "latitude": 26.9124,
        "longitude": 75.7873
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["zodiac"] == "Leo"

def test_cache_stats():
    """Test cache statistics endpoint"""
    response = client.get("/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "cache_enabled" in data

def test_clear_cache():
    """Test cache clearing endpoint"""
    response = client.delete("/cache")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_multiple_zodiac_signs():
    """Test different zodiac signs"""
    test_cases = [
        ("1990-03-25", "Aries"),
        ("1990-05-15", "Taurus"),
        ("1990-07-15", "Cancer"),
        ("1990-12-25", "Capricorn"),
    ]
    
    for birth_date, expected_zodiac in test_cases:
        payload = {
            "name": "Test",
            "birth_date": birth_date,
            "birth_time": "12:00",
            "birth_place": "Test"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["zodiac"] == expected_zodiac

@pytest.mark.asyncio
async def test_async_cache_operations():
    """Test async cache operations directly"""
    # This test requires pytest-asyncio
    user_id = "test_async_user"
    
    # Test set and get user profile
    profile = {"score": 5.0, "insights_count": 3}
    await cache_service.set_user_profile(user_id, profile)
    
    retrieved_profile = await cache_service.get_user_profile(user_id)
    assert retrieved_profile is not None
    assert retrieved_profile["score"] == 5.0
    
    # Test update score
    await cache_service.update_user_score(user_id, 2.0)
    updated_profile = await cache_service.get_user_profile(user_id)
    assert updated_profile["score"] == 7.0

def test_caching_behavior():
    """Test that caching works correctly"""
    payload = {
        "name": "TestUser",
        "birth_date": "1990-01-15",
        "birth_time": "12:00",
        "birth_place": "Test City"
    }
    
    # First request - may be cache miss
    response1 = client.post("/predict", json=payload)
    assert response1.status_code == 200
    data1 = response1.json()
    insight1 = data1["insight"]
    
    # Second request - should be cache hit (same zodiac, same day)
    response2 = client.post("/predict", json=payload)
    assert response2.status_code == 200
    data2 = response2.json()
    insight2 = data2["insight"]
    
    # Insights should be the same (cached)
    assert insight1 == insight2
    # Note: cache_hit may not be True for first request if cache was empty

@patch('app.services.llm_service.llm_service.client')
def test_llm_fallback(mock_openai_client):
    """Test that fallback works when LLM fails"""
    # Mock async OpenAI client to raise an error
    mock_completion = AsyncMock()
    mock_completion.create.side_effect = Exception("API Error")
    mock_openai_client.chat.completions = mock_completion
    
    payload = {
        "name": "TestUser",
        "birth_date": "1995-08-20",
        "birth_time": "14:30",
        "birth_place": "Test"
    }
    
    # Should still work with fallback
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "insight" in data
    assert len(data["insight"]) > 0

if __name__ == "__main__":
    print("Running async service tests...")
    print("\nNote: Some tests require Redis and OpenAI API key to be configured.")
    print("Set REDIS_HOST, REDIS_PORT, and OPENAI_API_KEY in environment or .env file.\n")
    
    try:
        # Run synchronous tests
        test_read_main()
        test_health_check()
        test_predict_insight()
        test_predict_insight_with_user_id()
        test_predict_insight_with_language()
        test_predict_insight_with_coordinates()
        test_cache_stats()
        test_clear_cache()
        test_multiple_zodiac_signs()
        test_caching_behavior()
        
        # Run async test
        asyncio.run(test_async_cache_operations())
        
        print("✅ All tests passed!")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

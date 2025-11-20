"""
Comprehensive test script for Cohere integration
Tests all services: LLM, Translation, Vector Store, and Cache
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_imports():
    """Test that all required modules can be imported"""
    print("=" * 60)
    print("TEST 1: Testing Imports")
    print("=" * 60)
    
    try:
        import cohere
        print("✓ Cohere SDK imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import cohere: {e}")
        return False
    
    try:
        import faiss
        print(f"✓ FAISS imported successfully (version: {faiss.__version__})")
    except ImportError as e:
        print(f"✗ Failed to import faiss: {e}")
        return False
    
    try:
        from app.config import settings
        print("✓ Config imported successfully")
        print(f"  - Cohere Model: {settings.COHERE_MODEL}")
        print(f"  - Embedding Model: {settings.COHERE_EMBEDDING_MODEL}")
        print(f"  - Vector Store Enabled: {settings.VECTOR_STORE_ENABLED}")
    except ImportError as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    try:
        from app.services.llm_service import llm_service
        print("✓ LLM Service imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import LLM service: {e}")
        return False
    
    try:
        from app.services.translation import translation_service
        print("✓ Translation Service imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Translation service: {e}")
        return False
    
    try:
        from app.services.vector_store import vector_store
        print("✓ Vector Store imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Vector Store: {e}")
        return False
    
    try:
        from app.services.cache import cache_service
        print("✓ Cache Service imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import Cache service: {e}")
        return False
    
    print("\n✓ All imports successful!\n")
    return True


async def test_cache_service():
    """Test in-memory cache functionality"""
    print("=" * 60)
    print("TEST 2: Testing In-Memory Cache Service")
    print("=" * 60)
    
    try:
        from app.services.cache import cache_service
        from datetime import date
        
        # Test setting and getting daily insight
        test_zodiac = "Aries"
        test_insight = "Test insight for Aries"
        test_date = date.today()
        
        await cache_service.set_daily_insight(test_zodiac, test_insight, test_date)
        cached = await cache_service.get_daily_insight(test_zodiac, test_date)
        
        assert cached == test_insight, f"Expected '{test_insight}', got '{cached}'"
        print(f"✓ Daily insight caching works")
        
        # Test user profile
        test_user_id = "test_user_123"
        test_profile = {"name": "Test User", "score": 10.5}
        
        await cache_service.set_user_profile(test_user_id, test_profile)
        profile = await cache_service.get_user_profile(test_user_id)
        
        assert profile == test_profile, f"Expected {test_profile}, got {profile}"
        print(f"✓ User profile caching works")
        
        # Test cache stats
        stats = await cache_service.get_cache_stats()
        print(f"✓ Cache stats retrieved: {stats}")
        assert stats["cache_backend"] == "in-memory", "Cache backend should be in-memory"
        
        # Test clear cache
        await cache_service.clear_cache()
        cached_after_clear = await cache_service.get_daily_insight(test_zodiac, test_date)
        assert cached_after_clear is None, "Cache should be empty after clear"
        print(f"✓ Cache clearing works")
        
        print("\n✓ All cache tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Cache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_service_initialization():
    """Test that services initialize properly without API key"""
    print("=" * 60)
    print("TEST 3: Testing Service Initialization (No API Key)")
    print("=" * 60)
    
    try:
        from app.services.llm_service import llm_service
        from app.services.translation import translation_service
        from app.services.vector_store import vector_store
        
        # Without API key, clients should be None but services should still work
        print(f"✓ LLM Service client status: {llm_service.client is not None}")
        print(f"✓ Translation Service client status: {translation_service.client is not None}")
        print(f"✓ Vector Store client status: {vector_store.client is not None}")
        
        # Test fallback functionality
        fallback_insight = llm_service._get_fallback_insight("TestUser", "Leo", None)
        assert "Leo" in fallback_insight or "TestUser" in fallback_insight, "Fallback should include zodiac or name"
        print(f"✓ LLM fallback works: '{fallback_insight[:50]}...'")
        
        print("\n✓ All service initialization tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Service initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_vector_store_structure():
    """Test vector store structure and corpus loading"""
    print("=" * 60)
    print("TEST 4: Testing Vector Store Structure")
    print("=" * 60)
    
    try:
        from app.services.vector_store import vector_store
        import os
        
        # Check if corpus file exists
        corpus_path = os.path.join(os.path.dirname(__file__), "app", "data", "astrological_corpus.json")
        if os.path.exists(corpus_path):
            print(f"✓ Corpus file found at: {corpus_path}")
            
            import json
            with open(corpus_path, 'r') as f:
                data = json.load(f)
                insights_count = len(data.get("insights", []))
                print(f"✓ Corpus contains {insights_count} insights")
        else:
            print(f"⚠ Corpus file not found at: {corpus_path}")
            print("  This is expected if corpus hasn't been created yet")
        
        print(f"✓ Vector store dimension: {vector_store.dimension}")
        assert vector_store.dimension == 1024, "Cohere embed-english-v3.0 should have dimension 1024"
        
        print("\n✓ Vector store structure tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Vector store structure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_config():
    """Test configuration settings"""
    print("=" * 60)
    print("TEST 5: Testing Configuration")
    print("=" * 60)
    
    try:
        from app.config import settings
        
        # Check Cohere settings
        assert hasattr(settings, 'COHERE_API_KEY'), "Missing COHERE_API_KEY"
        print(f"✓ COHERE_API_KEY configured: {bool(settings.COHERE_API_KEY)}")
        
        assert hasattr(settings, 'COHERE_MODEL'), "Missing COHERE_MODEL"
        print(f"✓ COHERE_MODEL: {settings.COHERE_MODEL}")
        
        assert hasattr(settings, 'COHERE_EMBEDDING_MODEL'), "Missing COHERE_EMBEDDING_MODEL"
        print(f"✓ COHERE_EMBEDDING_MODEL: {settings.COHERE_EMBEDDING_MODEL}")
        
        # Check removed settings
        assert not hasattr(settings, 'OPENAI_API_KEY'), "OPENAI_API_KEY should be removed"
        assert not hasattr(settings, 'REDIS_HOST'), "REDIS_HOST should be removed"
        print("✓ Old OpenAI and Redis configs removed")
        
        print("\n✓ All configuration tests passed!\n")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("COHERE INTEGRATION TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Imports", await test_imports()))
    results.append(("Cache Service", await test_cache_service()))
    results.append(("Service Initialization", await test_service_initialization()))
    results.append(("Vector Store Structure", await test_vector_store_structure()))
    results.append(("Configuration", await test_config()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Cohere integration is complete.\n")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the errors above.\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)


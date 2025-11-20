import logging
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query, HTTPException
from app.models import BirthDetails, InsightResponse
from app.services.zodiac import get_zodiac_sign
from app.services.insight import generate_insight
from app.services.cache import cache_service
from app.services.vector_store import vector_store
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Initializing services...")
    await vector_store.initialize()
    logger.info("Services initialized")
    yield
    # Shutdown
    logger.info("Closing connections...")
    await cache_service.close()
    logger.info("Connections closed")

app = FastAPI(
    title="Astrological Insight Generator",
    description="Generate personalized daily astrological insights using Cohere LLM and vector store (Async)",
    version="3.0.0",
    lifespan=lifespan
)

@app.post("/predict", response_model=InsightResponse)
async def predict_insight(
    details: BirthDetails,
    language: str = Query("en", description="Language code (en, hi)")
):
    """
    Generate personalized astrological insight (async)
    
    Args:
        details: Birth details including name, date, time, and place
        language: Target language code (default: "en", supports "hi")
        
    Returns:
        InsightResponse with zodiac sign, insight text, and metadata
    """
    try:
        # Auto-generate user_id if not provided
        user_id = details.user_id if details.user_id else str(uuid.uuid4())
        
        # Get zodiac sign
        zodiac_sign = get_zodiac_sign(details.birth_date)
        
        # Generate insight (async)
        insight_text, cache_hit = await generate_insight(
            name=details.name,
            zodiac=zodiac_sign,
            language=language,
            user_id=user_id,
            birth_details=details
        )
        
        # Get user score
        user_score = None
        user_profile = await cache_service.get_user_profile(user_id)
        if user_profile:
            user_score = user_profile.get("score", 0)
        
        return InsightResponse(
            zodiac=zodiac_sign,
            insight=insight_text,
            language=language,
            cache_hit=cache_hit,
            user_score=user_score,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error generating insight: {e}")
        raise

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Astrological Insight Generator (Async). Use /predict to get insights.",
        "version": "3.0.0",
        "features": ["In-Memory Cache", "Cohere LLM", "Cohere Embeddings", "FAISS Vector Store", "Async"],
        "endpoints": {
            "/predict": "POST - Generate astrological insight",
            "/user/{user_id}": "GET - Get user profile",
            "/health": "GET - Health check",
            "/cache/stats": "GET - Cache statistics"
        }
    }

@app.get("/user/{user_id}")
async def get_user_profile(user_id: str):
    """
    Get user profile by user_id
    
    Args:
        user_id: User identifier
        
    Returns:
        User profile with birth details, score, insights_count, and past insights
    """
    profile = await cache_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "cache": "in-memory (async)",
            "vector_store": "faiss + cohere embeddings (async)",
            "llm": "cohere command-r (async)",
            "translation": "cohere (async)"
        }
    }

@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics (async)"""
    return await cache_service.get_cache_stats()

@app.delete("/cache")
async def clear_cache():
    """Clear all caches (async)"""
    await cache_service.clear_cache()
    return {"message": "Cache cleared successfully"}

import logging
from datetime import date
from typing import Optional
from app.services.llm_service import llm_service
from app.services.cache import cache_service
from app.services.vector_store import vector_store
from app.services.translation import translation_service
from app.config import settings

logger = logging.getLogger(__name__)

async def generate_insight(
    name: str,
    zodiac: str,
    language: str = "en",
    user_id: Optional[str] = None,
    target_date: Optional[date] = None,
    birth_details: Optional[any] = None
) -> tuple[str, bool]:
    """
    Generate personalized astrological insight (async)
    
    This function orchestrates:
    1. Cache lookup
    2. User profile retrieval
    3. Vector store retrieval for context
    4. LLM generation
    5. Translation (if needed)
    6. Cache storage
    
    Args:
        name: User's name
        zodiac: Zodiac sign
        language: Target language code (default: "en")
        user_id: Optional user ID for personalization
        target_date: Optional target date (defaults to today)
        birth_details: Optional birth details object (BirthDetails model)
        
    Returns:
        Tuple of (insight_text, cache_hit)
    """
    if target_date is None:
        target_date = date.today()
    
    # Check cache first
    cached_insight = ""
    # await cache_service.get_daily_insight(zodiac, target_date)
    if cached_insight:
        logger.info(f"Cache hit for {zodiac} on {target_date}")
        
        # Translate if needed
        if language != "en":
            cached_insight = translation_service.translate(cached_insight, language)
        
        # Record user interaction
        if user_id:
            # Pass birth details if available
            kwargs = {"user_id": user_id, "zodiac": zodiac, "insight": cached_insight}
            if birth_details:
                kwargs.update({
                    "name": birth_details.name,
                    "birth_date": birth_details.birth_date,
                    "birth_time": birth_details.birth_time,
                    "birth_place": birth_details.birth_place,
                    "latitude": birth_details.latitude,
                    "longitude": birth_details.longitude
                })
            await cache_service.record_user_insight(**kwargs)
            await cache_service.update_user_score(user_id, 0.5)  # Lower score for cached insights
        
        return cached_insight, True
    
    # Cache miss - generate new insight
    logger.info(f"Generating new insight for {name} ({zodiac})")
    
    # Retrieve user profile for personalization
    user_profile = None
    if user_id:
        user_profile = await cache_service.get_user_profile(user_id)
        if user_profile:
            logger.info(f"Using user profile for personalization (score: {user_profile.get('score', 0)}, insights: {user_profile.get('insights_count', 0)})")
    
    # Retrieve context from vector store
    context_texts = []
    if settings.VECTOR_STORE_ENABLED:
        try:
            # Enhance query with user preferences if available
            query = f"{zodiac} daily horoscope insight"
            
            # Personalize query based on user profile
            if user_profile and user_profile.get("past_insights"):
                past_insights = user_profile.get("past_insights", [])
                
                # Extract themes from past insights to improve search relevance
                if len(past_insights) > 0:
                    # Build a more personalized query using keywords from past insights
                    recent_insight = past_insights[-1].get("insight", "")
                    # Extract key words that might indicate user interests (career, love, health, etc.)
                    query_keywords = []
                    if any(word in recent_insight.lower() for word in ["career", "work", "job", "professional"]):
                        query_keywords.append("career")
                    if any(word in recent_insight.lower() for word in ["love", "relationship", "partner", "romance"]):
                        query_keywords.append("love")
                    if any(word in recent_insight.lower() for word in ["health", "wellness", "energy", "body"]):
                        query_keywords.append("health")
                    if any(word in recent_insight.lower() for word in ["finance", "money", "financial", "wealth"]):
                        query_keywords.append("finance")
                    
                    if query_keywords:
                        query = f"{zodiac} {' '.join(query_keywords)} daily horoscope insight"
                    else:
                        query = f"{zodiac} personalized daily horoscope insight"
            
            results = await vector_store.search(query, zodiac=zodiac, top_k=settings.TOP_K_RESULTS)
            context_texts = [r["text"] for r in results]
            
            if not context_texts:
                # Fallback: get zodiac-specific insights
                context_texts = vector_store.get_zodiac_insights(zodiac, limit=3)
        except Exception as e:
            logger.warning(f"Error retrieving vector store context: {e}")
    
    # Generate insight using LLM with user profile
    try:
        insight = await llm_service.generate_insight(
            name=name,
            zodiac=zodiac,
            context=context_texts if context_texts else None,
            user_profile=user_profile,
            use_fallback=True
        )
    except Exception as e:
        logger.error(f"Error generating insight: {e}")
        # Fallback to simple template
        insight = f"{name}, your {zodiac} energy is strong today. Trust your intuition and embrace the opportunities that come your way."
    
    # Translate if needed
    if language != "en":
        insight = translation_service.translate(insight, language)
    
    # Cache the insight
    await cache_service.set_daily_insight(zodiac, insight, target_date)
    
    # Record user interaction for personalization
    if user_id:
        # Pass birth details if available
        kwargs = {"user_id": user_id, "zodiac": zodiac, "insight": insight}
        if birth_details:
            kwargs.update({
                "name": birth_details.name,
                "birth_date": birth_details.birth_date,
                "birth_time": birth_details.birth_time,
                "birth_place": birth_details.birth_place,
                "latitude": birth_details.latitude,
                "longitude": birth_details.longitude
            })
        await cache_service.record_user_insight(**kwargs)
        await cache_service.update_user_score(user_id, 1.0)
    
    return insight, False

from datetime import datetime, date
from typing import Optional, Dict, Any
import uuid

class AsyncCacheService:
    """Simple in-memory cache service for insights and user data"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    async def get_daily_insight(self, zodiac_sign: str, target_date: Optional[date] = None) -> Optional[str]:
        """
        Get cached daily insight for a zodiac sign
        
        Args:
            zodiac_sign: Zodiac sign
            target_date: Target date (defaults to today)
            
        Returns:
            Cached insight or None if not found
        """
        if target_date is None:
            target_date = date.today()
        
        cache_key = f"insight:daily:{zodiac_sign}:{target_date.isoformat()}"
        return self._cache.get(cache_key)
    
    async def set_daily_insight(self, zodiac_sign: str, insight: str, target_date: Optional[date] = None):
        """
        Cache daily insight for a zodiac sign
        
        Args:
            zodiac_sign: Zodiac sign
            insight: Insight text to cache
            target_date: Target date (defaults to today)
        """
        if target_date is None:
            target_date = date.today()
        
        cache_key = f"insight:daily:{zodiac_sign}:{target_date.isoformat()}"
        self._cache[cache_key] = insight
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached user profile
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile dict or None if not found
        """
        cache_key = f"user:profile:{user_id}"
        return self._cache.get(cache_key)
    
    async def set_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """
        Cache user profile
        
        Args:
            user_id: User identifier
            profile: User profile data
        """
        cache_key = f"user:profile:{user_id}"
        self._cache[cache_key] = profile
    
    async def create_user_profile(
        self,
        user_id: str,
        name: str,
        birth_date: date,
        birth_time: str,
        birth_place: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        zodiac: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new user profile with birth details
        
        Args:
            user_id: User identifier
            name: User's name
            birth_date: Birth date
            birth_time: Birth time
            birth_place: Birth place
            latitude: Optional latitude
            longitude: Optional longitude
            zodiac: Optional zodiac sign
            
        Returns:
            Created user profile
        """
        profile = {
            "user_id": user_id,
            "name": name,
            "birth_date": birth_date.isoformat(),
            "birth_time": birth_time,
            "birth_place": birth_place,
            "score": 0,
            "insights_count": 0,
            "past_insights": [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        if latitude is not None:
            profile["latitude"] = latitude
        if longitude is not None:
            profile["longitude"] = longitude
        if zodiac:
            profile["preferred_zodiac"] = zodiac
            
        await self.set_user_profile(user_id, profile)
        return profile
    
    async def update_user_score(self, user_id: str, score_delta: float = 1.0):
        """
        Update user's preference score
        
        Args:
            user_id: User identifier
            score_delta: Amount to add to score
        """
        profile = await self.get_user_profile(user_id)
        if profile:
            profile["score"] = profile.get("score", 0) + score_delta
            profile["last_updated"] = datetime.now().isoformat()
            await self.set_user_profile(user_id, profile)
        else:
            await self.set_user_profile(user_id, {
                "score": score_delta,
                "last_updated": datetime.now().isoformat(),
                "insights_count": 0
            })
    
    async def record_user_insight(
        self,
        user_id: str,
        zodiac: str,
        insight: str,
        name: Optional[str] = None,
        birth_date: Optional[date] = None,
        birth_time: Optional[str] = None,
        birth_place: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ):
        """
        Record an insight for a user (for personalization)
        
        Args:
            user_id: User identifier
            zodiac: Zodiac sign
            insight: Insight text
            name: Optional user's name (stored if profile doesn't exist)
            birth_date: Optional birth date (stored if profile doesn't exist)
            birth_time: Optional birth time (stored if profile doesn't exist)
            birth_place: Optional birth place (stored if profile doesn't exist)
            latitude: Optional latitude (stored if profile doesn't exist)
            longitude: Optional longitude (stored if profile doesn't exist)
        """
        profile = await self.get_user_profile(user_id)
        if not profile:
            # Create new profile with birth details if provided
            profile = {
                "user_id": user_id,
                "score": 0,
                "insights_count": 0,
                "past_insights": [],
                "preferred_zodiac": zodiac,
                "created_at": datetime.now().isoformat()
            }
            
            # Store birth details if provided
            if name:
                profile["name"] = name
            if birth_date:
                profile["birth_date"] = birth_date.isoformat()
            if birth_time:
                profile["birth_time"] = birth_time
            if birth_place:
                profile["birth_place"] = birth_place
            if latitude is not None:
                profile["latitude"] = latitude
            if longitude is not None:
                profile["longitude"] = longitude
        
        profile["insights_count"] = profile.get("insights_count", 0) + 1
        past_insights = profile.get("past_insights", [])
        past_insights.append({
            "zodiac": zodiac,
            "insight": insight,
            "timestamp": datetime.now().isoformat()
        })
        profile["past_insights"] = past_insights[-10:]
        profile["last_updated"] = datetime.now().isoformat()
        
        await self.set_user_profile(user_id, profile)
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_enabled": True,
            "cache_backend": "in-memory",
            "total_keys": len(self._cache)
        }
    
    async def clear_cache(self):
        """Clear all caches"""
        self._cache.clear()
    
    async def close(self):
        """Close cache (no-op for in-memory cache)"""
        pass

# Singleton instance
cache_service = AsyncCacheService()

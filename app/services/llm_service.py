import logging
from typing import Optional, List
import cohere
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback templates if LLM fails
FALLBACK_TEMPLATES = {
    "Aries": [
        "Your fiery Aries energy is strong today. Take bold action on your goals.",
        "As an Aries, you're feeling particularly driven. Channel this energy into productive pursuits.",
    ],
    "Taurus": [
        "Your grounded Taurus nature will help you stay steady through any challenges today.",
        "As a Taurus, focus on stability and comfort. Trust your practical instincts.",
    ],
    "Gemini": [
        "Your curious Gemini mind is buzzing with ideas today. Share your thoughts with others.",
        "As a Gemini, communication is key. Express yourself clearly and listen actively.",
    ],
    "Cancer": [
        "Your intuitive Cancer nature is heightened today. Trust your emotional intelligence.",
        "As a Cancer, focus on nurturing relationships and creating a safe space for yourself.",
    ],
    "Leo": [
        "Your innate leadership and warmth will shine today. Embrace spontaneity and avoid overthinking.",
        "As a Leo, your natural charisma is at its peak. Share your light with others.",
    ],
    "Virgo": [
        "Your analytical Virgo mind will help you solve complex problems today.",
        "As a Virgo, attention to detail is your strength. Use it to improve your daily routines.",
    ],
    "Libra": [
        "Your diplomatic Libra nature will help you find balance in relationships today.",
        "As a Libra, seek harmony and beauty. Make time for things that bring you joy.",
    ],
    "Scorpio": [
        "Your intense Scorpio energy is focused today. Dive deep into what matters most.",
        "As a Scorpio, your transformative power is strong. Embrace change and growth.",
    ],
    "Sagittarius": [
        "Your adventurous Sagittarius spirit is calling. Explore new ideas and perspectives.",
        "As a Sagittarius, your optimism will carry you through. Keep your eyes on the horizon.",
    ],
    "Capricorn": [
        "Your disciplined Capricorn nature will help you achieve your goals today.",
        "As a Capricorn, focus on long-term planning. Your hard work is paying off.",
    ],
    "Aquarius": [
        "Your innovative Aquarius mind is full of unique ideas today. Share your vision.",
        "As an Aquarius, your humanitarian spirit is strong. Connect with your community.",
    ],
    "Pisces": [
        "Your intuitive Pisces nature is guiding you today. Trust your inner voice.",
        "As a Pisces, your creativity and empathy are heightened. Express yourself authentically.",
    ],
}

class AsyncLLMService:
    """Async service for generating insights using Cohere LLM"""
    
    def __init__(self):
        self.client = None
        if settings.COHERE_API_KEY:
            try:
                self.client = cohere.AsyncClient(api_key=settings.COHERE_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere client: {e}")
    
    async def generate_insight(
        self,
        name: str,
        zodiac: str,
        context: Optional[List[str]] = None,
        user_profile: Optional[dict] = None,
        use_fallback: bool = True
    ) -> str:
        """
        Generate personalized astrological insight using Cohere LLM (async)
        
        Args:
            name: User's name
            zodiac: Zodiac sign
            context: Optional list of context strings from vector store
            user_profile: Optional user profile dict with preferences and history
            use_fallback: Whether to use fallback templates if LLM fails
            
        Returns:
            Generated insight text
        """
        if not self.client:
            logger.warning("Cohere client not initialized, using fallback")
            return self._get_fallback_insight(name, zodiac, user_profile)
        
        try:
            prompt = self._build_prompt(name, zodiac, context, user_profile)
            preamble = "You are an expert astrologer who provides personalized, warm, and insightful daily horoscopes. Keep responses concise (1-2 sentences) and encouraging."
            
            response = await self.client.chat(
                model=settings.COHERE_MODEL,
                message=prompt,
                preamble=preamble,
                temperature=settings.COHERE_TEMPERATURE,
                max_tokens=settings.COHERE_MAX_TOKENS
            )
            
            insight = response.text.strip()
            logger.info(f"Generated insight for {name} ({zodiac})")
            return insight
            
        except Exception as e:
            logger.error(f"Error generating insight with LLM: {e}")
            if use_fallback:
                return self._get_fallback_insight(name, zodiac, user_profile)
            raise
    
    def _build_prompt(
        self, 
        name: str, 
        zodiac: str, 
        context: Optional[List[str]], 
        user_profile: Optional[dict] = None
    ) -> str:
        """Build the prompt for LLM with user profile personalization"""
        prompt = f"Generate a personalized daily astrological insight for {name}, who is a {zodiac}."
        
        # Include user profile information for personalization
        if user_profile:
            insights_count = user_profile.get("insights_count", 0)
            past_insights = user_profile.get("past_insights", [])
            preferred_zodiac = user_profile.get("preferred_zodiac")
            
            if insights_count > 0:
                prompt += f"\n\nThis user has requested {insights_count} insight(s) before."
            
            # Use past insights to understand user preferences
            if past_insights:
                # Extract common themes or categories from past insights
                prompt += "\n\nConsider their past insights to maintain consistency and build on previous guidance:"
                # Show last 2-3 insights for context
                recent_insights = past_insights[-3:]
                for i, past in enumerate(recent_insights, 1):
                    prompt += f"\n- Previous insight: {past.get('insight', '')[:100]}..."
            
            if preferred_zodiac and preferred_zodiac == zodiac:
                prompt += "\n\nThis is their preferred zodiac sign, so make the insight particularly meaningful."
        
        if context:
            prompt += "\n\nConsider these related astrological insights:\n"
            for i, ctx in enumerate(context, 1):
                prompt += f"{i}. {ctx}\n"
        
        prompt += "\nMake it personal, warm, and specific to their zodiac sign. Keep it to 1-2 sentences."
        return prompt
    
    def _get_fallback_insight(self, name: str, zodiac: str, user_profile: Optional[dict] = None) -> str:
        """Get fallback insight from templates, with personalization if user profile available"""
        import random
        templates = FALLBACK_TEMPLATES.get(zodiac, [
            f"{name}, trust your intuition today. The stars are aligned in your favor."
        ])
        
        # If user profile exists, try to personalize the selection
        if user_profile and user_profile.get("past_insights"):
            past_insights = user_profile.get("past_insights", [])
            # If user has history, use a different template to show variety
            # This simulates personalization even in fallback mode
            if len(past_insights) > 2:
                # Use a different template index for returning users
                template_index = len(past_insights) % len(templates)
                template = templates[template_index]
            else:
                template = random.choice(templates)
        else:
            template = random.choice(templates)
        
        result = template.replace("{name}", name) if "{name}" in template else f"{name}, {template}"
        
        # Add personalization note if user has history
        if user_profile and user_profile.get("insights_count", 0) > 1:
            result += " Based on your journey, continue trusting your path."
        
        return result

# Singleton instance
llm_service = AsyncLLMService()

import logging
import cohere
from app.config import settings

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for translating insights to Hindi and other languages using Cohere"""
    
    def __init__(self):
        self.client = None
        if settings.COHERE_API_KEY:
            try:
                self.client = cohere.Client(api_key=settings.COHERE_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere client: {e}")
    
    def translate(self, text: str, target_lang: str = "hi", source_lang: str = "en") -> str:
        """
        Translate text to target language using Cohere
        
        Args:
            text: Text to translate
            target_lang: Target language code (e.g., 'hi' for Hindi)
            source_lang: Source language code (default: 'en')
            
        Returns:
            Translated text or original text if translation fails
        """
        if target_lang == source_lang or target_lang == "en":
            return text
        
        if not self.client:
            logger.warning("Cohere client not initialized, returning original text")
            return text
        
        try:
            # Map language codes to full names
            lang_map = {
                "hi": "Hindi",
                "ta": "Tamil",
                "te": "Telugu",
            }
            
            target_language = lang_map.get(target_lang, target_lang)
            
            prompt = f"Translate the following English text to {target_language}. Only provide the translation, nothing else:\n\n{text}"
            
            response = self.client.chat(
                model=settings.COHERE_MODEL,
                message=prompt,
                temperature=0.3,  # Lower temperature for more accurate translation
                max_tokens=300
            )
            
            translated = response.text.strip()
            logger.info(f"Translated text to {target_language}")
            return translated
            
        except Exception as e:
            logger.error(f"Error translating text: {e}")
            return text
    
    def is_language_supported(self, lang_code: str) -> bool:
        """Check if a language is supported"""
        supported_languages = ["en", "hi", "ta", "te"]
        return lang_code in supported_languages

# Singleton instance
translation_service = TranslationService()


import json
import logging
import os
from typing import List, Dict
import numpy as np
import faiss
import cohere
from app.config import settings

logger = logging.getLogger(__name__)

class AsyncVectorStore:
    """Async vector store using Cohere embeddings and FAISS for similarity search"""
    
    def __init__(self):
        self.client = None
        self.corpus = []
        self.index = None
        self.dimension = 1024  # Cohere embed-english-v3.0 embedding dimension
        self._initialized = False
        
        if settings.VECTOR_STORE_ENABLED and settings.COHERE_API_KEY:
            self.client = cohere.AsyncClient(api_key=settings.COHERE_API_KEY)
    
    async def initialize(self):
        """Initialize the vector store with corpus and embeddings"""
        if self._initialized:
            return
        
        try:
            # Load corpus
            current_dir = os.path.dirname(__file__)
            app_dir = os.path.dirname(current_dir)
            project_root = os.path.dirname(app_dir)
            corpus_path = os.path.join(project_root, "app", "data", "astrological_corpus.json")
            
            if os.path.exists(corpus_path):
                with open(corpus_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.corpus = data.get("insights", [])
            else:
                logger.warning(f"Corpus file not found at {corpus_path}, using empty corpus")
                self.corpus = []
            
            # Initialize FAISS index and build embeddings
            if self.corpus and self.client:
                try:
                    await self._build_embeddings()
                    self._initialized = True
                    logger.info(f"Vector store initialized with {len(self.corpus)} insights using Cohere embeddings")
                except Exception as e:
                    logger.error(f"Failed to initialize embeddings: {e}")
                    self.client = None
            else:
                logger.warning("No corpus data or Cohere client unavailable, vector store disabled")
                
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self._initialized = False
    
    async def _build_embeddings(self):
        """Build embeddings for all corpus texts using Cohere"""
        if not self.client or not self.corpus:
            return
        
        try:
            texts = [item["text"] for item in self.corpus]
            
            # Get embeddings from Cohere (batch processing)
            logger.info(f"Generating embeddings for {len(texts)} texts...")
            response = await self.client.embed(
                model=settings.COHERE_EMBEDDING_MODEL,
                texts=texts,
                input_type="search_document"
            )
            
            # Extract embeddings
            embeddings_array = np.array(response.embeddings, dtype='float32')
            
            # Create FAISS index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings_array)
            
            logger.info(f"Built FAISS index with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Error building embeddings: {e}")
            self.index = None
    
    async def search(self, query: str, zodiac: str = None, top_k: int = None) -> List[Dict[str, any]]:
        """
        Search for similar insights in the corpus using Cohere embeddings
        
        Args:
            query: Search query text
            zodiac: Optional zodiac sign to filter results
            top_k: Number of results to return (defaults to config value)
            
        Returns:
            List of similar insights with scores
        """
        if not self._initialized:
            await self.initialize()
        
        if not self._initialized or self.index is None or not self.client:
            logger.debug("Vector store not initialized, returning empty results")
            return []
        
        if top_k is None:
            top_k = settings.TOP_K_RESULTS
        
        try:
            # Get query embedding from Cohere
            response = await self.client.embed(
                model=settings.COHERE_EMBEDDING_MODEL,
                texts=[query],
                input_type="search_query"
            )
            query_embedding = np.array([response.embeddings[0]], dtype='float32')
            
            # Search FAISS index
            # Get more results than needed to filter by zodiac
            search_k = top_k * 3 if zodiac else top_k
            distances, indices = self.index.search(query_embedding, min(search_k, self.index.ntotal))
            
            # Build results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self.corpus):
                    continue
                
                item = self.corpus[idx]
                
                # Filter by zodiac if specified
                if zodiac and item.get("zodiac") != zodiac:
                    continue
                
                # Convert L2 distance to similarity score (inverse)
                similarity_score = 1 / (1 + float(dist))
                
                results.append({
                    "text": item["text"],
                    "zodiac": item.get("zodiac", "Unknown"),
                    "score": similarity_score,
                    "category": item.get("category", "general")
                })
                
                if len(results) >= top_k:
                    break
            
            logger.debug(f"Found {len(results)} similar insights for query: {query[:50]}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_zodiac_insights(self, zodiac: str, limit: int = 5) -> List[str]:
        """
        Get random insights for a specific zodiac sign (synchronous fallback)
        
        Args:
            zodiac: Zodiac sign
            limit: Maximum number of insights to return
            
        Returns:
            List of insight texts
        """
        if not self.corpus:
            return []
        
        zodiac_insights = [
            item["text"] for item in self.corpus
            if item.get("zodiac", "").lower() == zodiac.lower()
        ]
        
        import random
        return random.sample(zodiac_insights, min(limit, len(zodiac_insights)))

# Singleton instance
vector_store = AsyncVectorStore()

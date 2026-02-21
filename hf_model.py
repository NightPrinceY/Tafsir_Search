"""
Local SentenceTransformer wrapper - drop-in replacement for HF API.
Uses sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 locally.
Includes in-memory LRU embedding cache (cachetools).
"""
import logging
import threading
import numpy as np
from cachetools import TTLCache

logger = logging.getLogger(__name__)

EMBEDDING_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_model = None

# Embedding cache: deterministic — same text always yields the same vector
_embedding_cache = TTLCache(maxsize=1024, ttl=float('inf'))
_embedding_lock = threading.Lock()


def _get_model():
    global _model
    if _model is None:
        logger.info(f"Loading local SentenceTransformer model: {EMBEDDING_MODEL_NAME}")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


class HFEmbeddingModel:
    """Model-like object with encode() for use with retrieval.hybrid_search_fixed."""

    def encode(self, text, normalize_embeddings=True):
        """Encode text via local SentenceTransformer. Returns 1D numpy array."""
        cache_key = f"{text}::{normalize_embeddings}"

        with _embedding_lock:
            cached = _embedding_cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Tafsir embedding cache HIT: {text[:50]}...")
                return cached

        model = _get_model()
        emb = model.encode(text, convert_to_numpy=True)
        
        if emb.ndim == 2:
            emb = emb[0]
            
        if normalize_embeddings:
            norm = np.linalg.norm(emb)
            if norm > 0:
                emb = emb / norm

        with _embedding_lock:
            _embedding_cache[cache_key] = emb
        logger.debug(f"Tafsir embedding cache MISS → stored locally: {text[:50]}...")
        return emb

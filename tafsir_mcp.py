"""
MCP Tool: Tafsir Search (Hadith-style hybrid: BM25 + Semantic + Anchors)
Uses HF Inference API for embeddings (no local model).
"""
import sys
from pathlib import Path
import pickle
import logging
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
rag_initialized = False

df = None
tafsir_embeddings = None
bm25 = None
anchor_index = None
anchor_dict = None
unique_anchor_texts = None

TAFSIR_DIFFICULTY_MAPPING = {
    "تفسير الميسر": 1,
    "تفسير السعدي": 1,
    "تفسير الجلالين": 2,
    "تفسير ابن كثير": 2,
    "تفسير البغوي": 3,
    "تفسير القرطبي": 3,
    "تفسير الطبري": 4,
}


def safe_get(row, col: str, default=""):
    try:
        v = row.get(col, default) if hasattr(row, "get") else (row[col] if col in row else default)
        if v is None:
            return default
        if isinstance(v, float):
            import math
            if math.isnan(v):
                return default
        return str(v).strip()
    except Exception:
        return default


def short_preview(text: str, length: int = 300) -> str:
    text = (text or "").strip()
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "..."


def initialize_rag():
    global df, tafsir_embeddings, bm25, anchor_index, anchor_dict, unique_anchor_texts, rag_initialized
    if rag_initialized:
        return True
    try:
        import pandas as pd
        import numpy as np
        import faiss

        if not DATA_DIR.exists():
            logger.error(f"Data directory not found: {DATA_DIR}")
            return False

        df = pd.read_csv(DATA_DIR / "tafsir.csv", encoding="utf-8")
        try:
            tafsir_embeddings = np.load(DATA_DIR / "tafsir_embeddings.npy")
        except ValueError:
            tafsir_embeddings = np.load(DATA_DIR / "tafsir_embeddings.npy", allow_pickle=True)
        with open(DATA_DIR / "bm25.pkl", "rb") as f:
            bm25 = pickle.load(f)
        anchor_index = faiss.read_index(str(DATA_DIR / "faiss_anchor.index"))
        with open(DATA_DIR / "anchor_dict.pkl", "rb") as f:
            anchor_dict = pickle.load(f)
        with open(DATA_DIR / "unique_anchor_texts.pkl", "rb") as f:
            unique_anchor_texts = pickle.load(f)

        logger.info(f"Loaded tafsir: {len(df)} rows, embeddings {tafsir_embeddings.shape}")
        rag_initialized = True
        return True
    except Exception as e:
        logger.error(f"Failed to initialize tafsir RAG: {e}", exc_info=True)
        return False


try:
    initialize_rag()
except Exception as e:
    logger.error(f"Tafsir init error: {e}", exc_info=True)


async def get_tafsir(query: str, top_k: int = 5) -> Dict:
    """MCP Tool: Search tafsir by hybrid (BM25 + semantic + verse anchors)."""
    if not query or not str(query).strip():
        return {"tafsir_chunks": [], "error": "عَفْواً، السُّؤَالُ فَارِغٌ."}
    if not rag_initialized:
        return {"tafsir_chunks": [], "error": "عَفْواً، خِدْمَةُ التَّفْسِيرِ غَيْرُ مُتَاحَةٍ حَالِيَّاً."}
    try:
        from retrieval import hybrid_search_fixed
        from utils import preprocess_query, remove_tashkeel, remove_tafsir_stopwords
        from hf_model import HFEmbeddingModel

        model = HFEmbeddingModel()
        
        # Strip conversational/filler words first
        stripped_query = remove_tafsir_stopwords(query.strip())

        # Strip ONLY tashkeel so the semantic model
        # can properly match unvoweled corpus texts (without ruining letters like أ).
        cleaned_query = remove_tashkeel(stripped_query)
        
        results_df, debug = hybrid_search_fixed(
            query=cleaned_query,
            df=df,
            bm25=bm25,
            preprocess_query=preprocess_query,
            model=model,
            doc_embeddings=tafsir_embeddings,
            anchor_index=anchor_index,
            anchor_dict=anchor_dict,
            unique_anchor_texts=unique_anchor_texts,
            top_k=int(top_k),
            alpha_anchor=0.15,
            alpha_semantic=0.35,
            alpha_bm25=0.50
        )

        chunks = []
        for rank, (_, row) in enumerate(results_df.iterrows(), start=1):
            text = safe_get(row, "text")
            verses_keys = safe_get(row, "verses_keys")
            resource_name = safe_get(row, "resource_name")
            difficulty = TAFSIR_DIFFICULTY_MAPPING.get(resource_name, 2)
            chunks.append({
                "rank": rank,
                "text": text,
                "verses_keys": verses_keys,
                "resource_name": resource_name,
                "difficulty": difficulty
            })
        return {"tafsir_chunks": chunks, "error": None}
    except Exception as e:
        logger.error(f"Tafsir search error: {e}", exc_info=True)
        return {
            "tafsir_chunks": [],
            "error": f"عَفْواً، حَدَثَ خَطَأٌ: {str(e)[:100]}",
        }

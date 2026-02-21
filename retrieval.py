"""
Hybrid search for Tafsir (same architecture as Hadith):
BM25 + semantic (doc embeddings) + anchor (verse_key) with union optimization.
"""
import numpy as np


def query_anchor_scores(query, model, anchor_index, top_k=10):
    q_emb = model.encode(query, normalize_embeddings=True)
    scores, indices = anchor_index.search(q_emb.reshape(1, -1), top_k)
    return np.array(indices[0], dtype=int), np.array(scores[0], dtype=float)


def bm25_retrieve(query, bm25, preprocess_query, top_k=50):
    tokenized_query = preprocess_query(query)
    scores = bm25.get_scores(tokenized_query)
    top_idx = np.argsort(scores)[::-1][:top_k]
    return top_idx, scores[top_idx]


def compute_anchor_scores_for_docs(
    n_docs,
    anchor_indices,
    anchor_scores,
    anchor_dict,
    unique_anchor_texts,
):
    """Build per-doc anchor score vector. unique_anchor_texts[i] is the key for anchor_dict (e.g. verse_key)."""
    anchor_score_vec = np.zeros(n_docs, dtype=float)
    for a_idx, a_score in zip(anchor_indices, anchor_scores):
        if 0 <= a_idx < len(unique_anchor_texts):
            key = unique_anchor_texts[a_idx]
            for h_idx in anchor_dict.get(key, []):
                anchor_score_vec[h_idx] = a_score
    return anchor_score_vec


def hybrid_search_fixed(
    query,
    df,
    bm25,
    preprocess_query,
    model,
    doc_embeddings,
    anchor_index,
    anchor_dict,
    unique_anchor_texts,
    top_k=5,
    top_bm25=50,
    top_anchors=10,
    alpha_anchor=0.40,
    alpha_semantic=0.35,
    alpha_bm25=0.25,
    full_semantic=False,
):
    """
    Hybrid search: BM25 + anchor + semantic with union optimization.
    - doc_embeddings: (n_docs, dim) chunk/tafsir embeddings
    - unique_anchor_texts: list of keys for anchor_dict (e.g. verse_key), same order as FAISS index
    """
    n = len(df)
    eps = 1e-8

    bm25_indices, bm25_scores = bm25_retrieve(query, bm25, preprocess_query, top_k=top_bm25)
    bm25_map = {int(idx): float(score) for idx, score in zip(bm25_indices, bm25_scores)}

    anchor_idx, anchor_scores = query_anchor_scores(query, model, anchor_index, top_k=top_anchors)
    anchor_score_vec = compute_anchor_scores_for_docs(
        n_docs=n,
        anchor_indices=anchor_idx,
        anchor_scores=anchor_scores,
        anchor_dict=anchor_dict,
        unique_anchor_texts=unique_anchor_texts,
    )

    anchor_linked_indices = []
    for a_idx in anchor_idx:
        if 0 <= a_idx < len(unique_anchor_texts):
            key = unique_anchor_texts[int(a_idx)]
            anchor_linked_indices.extend(anchor_dict.get(key, []))
    anchor_linked_indices = np.unique(np.array(anchor_linked_indices, dtype=int)) if anchor_linked_indices else np.array([], dtype=int)

    if full_semantic:
        query_emb = model.encode(query, normalize_embeddings=True)
        semantic_scores_all = doc_embeddings @ query_emb
        semantic_score_vec = np.array(semantic_scores_all, dtype=float)
        union_indices = np.arange(n, dtype=int)
    else:
        union_indices = np.unique(np.concatenate([bm25_indices, anchor_linked_indices])).astype(int)
        query_emb = model.encode(query, normalize_embeddings=True)
        if len(union_indices) > 0:
            sem_vals = doc_embeddings[union_indices] @ query_emb
            semantic_score_vec = np.zeros(n, dtype=float)
            semantic_score_vec[union_indices] = sem_vals
        else:
            semantic_score_vec = np.zeros(n, dtype=float)

    bm25_score_vec = np.zeros(n, dtype=float)
    if bm25_map:
        bm25_vals = np.array(list(bm25_map.values()), dtype=float)
        bm25_max = float(bm25_vals.max()) if bm25_vals.size > 0 else 0.0
        for idx, val in bm25_map.items():
            bm25_score_vec[idx] = float(val / (bm25_max + eps)) if bm25_max > 0 else 0.0

    if np.max(anchor_scores) > 0:
        anchor_max = float(np.max(anchor_scores))
        if anchor_max > 0:
            anchor_score_vec = anchor_score_vec / (anchor_max + eps)

    sem_max = float(semantic_score_vec.max()) if semantic_score_vec.size > 0 else 0.0
    if sem_max > 0:
        semantic_score_vec = semantic_score_vec / (sem_max + eps)

    final_scores = (
        alpha_anchor * anchor_score_vec
        + alpha_semantic * semantic_score_vec
        + alpha_bm25 * bm25_score_vec
    )
    ranked_all = np.argsort(final_scores)[::-1]
    top_indices = ranked_all[:top_k]

    return df.iloc[top_indices].copy(), {
        "final_scores": final_scores,
        "anchor_scores": anchor_score_vec,
        "semantic_scores": semantic_score_vec,
        "bm25_scores": bm25_score_vec,
        "union_size": len(union_indices) if not full_semantic else n,
    }

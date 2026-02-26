---
title: Tafsir Search
emoji: 📚
colorFrom: yellow
colorTo: green
sdk: docker
pinned: false
license: mit
---

<div align="center">

# 📚 Tafsir Search

**Semantic search across 7 classical Quranic commentaries — find the exact scholarly interpretation you're looking for.**

[![HuggingFace Space](https://img.shields.io/badge/🤗%20HuggingFace-Live%20Demo-yellow?style=for-the-badge)](https://huggingface.co/spaces/NightPrince/Tafsir_Search)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-teal?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

</div>

---

## What Is This?

A hybrid AI-powered search engine over **~32,000 passages** from 7 major classical Tafsir (Quranic exegesis) books. Unlike simple keyword search, it understands the *meaning* of your query — returning the most relevant scholarly commentary even when the exact words don't appear.

Ask about a concept, a verse, a ruling, or a theological question in Arabic and get ranked excerpts from the scholars most likely to have addressed it.

---

## Demo

🔗 **[Live on HuggingFace Spaces →](https://huggingface.co/spaces/NightPrince/Tafsir_Search)**

---

## How It Works

```
User Query (Arabic)
      │
      ▼
┌─────────────────────────────────────────────┐
│           Arabic Preprocessing              │
│  Remove tashkeel · Normalize letters        │
│  Strip Tafsir-specific stopwords            │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│         Hybrid Search (3 signals)           │
│                                             │
│  ① BM25       50%  — keyword precision      │
│  ② Semantic   35%  — neural meaning match   │
│  ③ Anchor     15%  — verse-ref boosting     │
│                                             │
│  Corpus: ~32,000 Tafsir passages            │
│  Model: paraphrase-multilingual-MiniLM-L12  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
         Top-K ranked results
     (text · verse ref · difficulty)
```

The **anchor signal** embeds Quranic verse keys and boosts results linked to the verse most relevant to your query — making it verse-aware without hardcoding any mapping.

---

## Features

- **Hybrid retrieval** — BM25 + FAISS semantic + verse-anchor scoring
- **7 Tafsir sources** — spanning 1,200 years of Islamic scholarship
- **Difficulty levels** — from easy (الميسر) to classical Arabic (الطبري)
- **Verse references** — every result linked to its Quranic source
- **RTL Arabic UI** — glassmorphism design, fully right-to-left
- **Fast cold start** — model baked into Docker image at build time

---

## Tafsir Sources

| Difficulty | Book |
|---|---|
| ⭐ Easy | تفسير الميسر · تفسير السعدي |
| ⭐⭐ Medium | تفسير الجلالين · تفسير ابن كثير |
| ⭐⭐⭐ Advanced | تفسير البغوي · تفسير القرطبي |
| ⭐⭐⭐⭐ Classical | تفسير الطبري |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Vector Search | FAISS (CPU) |
| Keyword Search | BM25 (`rank-bm25`) |
| Frontend | Vanilla HTML/CSS/JS — RTL Arabic |
| Deployment | Docker on HuggingFace Spaces |

---

## Project Structure

```
├── app.py              # FastAPI entrypoint, /api/search endpoint
├── tafsir_mcp.py       # Search orchestrator, RAG initialization
├── retrieval.py        # Hybrid search: BM25 + semantic + anchor
├── hf_model.py         # Thread-safe SentenceTransformer + TTL cache
├── utils.py            # Arabic text utilities (tashkeel, normalization)
├── index.html          # Frontend UI
├── assets/
│   ├── script.js       # Fetch + render result cards
│   └── style.css       # Glassmorphism RTL design
├── data/
│   ├── tafsir.csv               # ~32k Tafsir passages (7 books)
│   ├── tafsir_embeddings.npy    # Pre-computed embeddings
│   ├── bm25.pkl                 # BM25 index
│   ├── faiss_anchor.index       # FAISS verse-anchor index
│   ├── anchor_dict.pkl          # verse_key → row indices
│   └── unique_anchor_texts.pkl  # Ordered verse key list
└── Dockerfile
```

---

## API

### `POST /api/search`

```json
// Request
{ "query": "حكم الغيبة وعقوبتها", "top_k": 5 }

// Response
{
  "results": [
    {
      "rank": 1,
      "text": "قال ابن كثير رحمه الله: الغيبة هي ذكرك أخاك بما يكره...",
      "verses_keys": "49:12",
      "resource_name": "تفسير ابن كثير",
      "difficulty": 2
    }
  ]
}
```

`top_k` accepts 1–10.

---

## Local Setup

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860 --reload
# open http://localhost:7860
```

---

## Built by

**يحيى النوساني** — [HuggingFace](https://huggingface.co/NightPrince)

---

*Part of a series of Islamic knowledge retrieval engines. See also: [Hadith Search](https://github.com/NightPrinceY/Hadith_Search) · [Quran Semantic Retrieval](https://github.com/NightPrinceY/Quran-Semantic-Retrieval)*

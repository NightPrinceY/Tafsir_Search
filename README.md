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

# 📚 Tafsir Search — مُحَرِّكُ بَحْثِ التَّفَاسِيرِ الهَجِين

**Ask a question in Arabic. Get the answer from the classical scholars of tafsir — at the level of difficulty that fits you.**

[![HuggingFace Space](https://img.shields.io/badge/🤗%20HuggingFace-Live%20Demo-yellow?style=for-the-badge)](https://huggingface.co/spaces/NightPrince/Tafsir_Search)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Python 3.10](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-teal?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)

</div>

---

## Table of Contents

1. [The idea in one paragraph](#1-the-idea-in-one-paragraph)
2. [The difficulty ladder — who each tafsir is for](#2-the-difficulty-ladder--who-each-tafsir-is-for)
3. [How a search works, step by step](#3-how-a-search-works-step-by-step)
4. [Every design idea, explained](#4-every-design-idea-explained)
5. [The data](#5-the-data)
6. [API](#6-api)
7. [Using it as a tool for a voice agent (MCP)](#7-using-it-as-a-tool-for-a-voice-agent-mcp)
8. [Run it yourself](#8-run-it-yourself)
9. [Project structure](#9-project-structure)
10. [The family of engines this belongs to](#10-the-family-of-engines-this-belongs-to)
11. [Known limitations](#11-known-limitations)
12. [Roadmap](#12-roadmap)

---

## 1. The idea in one paragraph

Most people who want to understand the Quran don't know **which verse** answers their question, and they don't know **which book of tafsir** to open. This engine solves both. You type a normal question — *"ما حكم الغيبة؟"* or *"ما معنى قوله تعالى الرجال قوامون على النساء"* — and it searches across **7 classical tafsir books at once**, ranks the passages that best answer you, and tells you **which verse** each passage explains and **how difficult** that book is to read.

> **بالعربي:** بدلاً من أن تبحث بنفسك في سبعة كتب تفسير وتعرف رقم الآية، اكتب سؤالك كما هو، وسيعطيك المحرك أنسب كلام المفسرين، مع رقم الآية ومستوى صعوبة الكتاب.

It was built as the tafsir engine behind **Muslim**, an Arabic voice AI companion, and also runs as a standalone web app.

---

## 2. The difficulty ladder — who each tafsir is for

Classical tafsir books are not equal in difficulty. Some were written for the general public in simple modern Arabic; others are deep scholarly works full of chains of narration (أسانيد), grammar debates, and juristic disputes. Giving a beginner a page of al-Tabari is like giving a first-year student a PhD thesis.

So **every result carries a difficulty level from 1 to 4**. This is the central idea of the project: *the same question deserves a different depth of answer for different people.*

| Level | Who it's for | Book | Why |
|:---:|---|---|---|
| ⭐ **1 — Easy** | Everyone, beginners, children, **voice assistants** | **التفسير الميسر** (al-Muyassar) | Written by a committee at the King Fahd Complex specifically to be short, clear, and in simple modern Arabic. One or two sentences per verse. |
| ⭐ **1 — Easy** | General readers who want a bit more | **تفسير السعدي** (as-Sa'di) | Simple language, but adds the lessons and guidance (الفوائد والهدايات) of each verse. |
| ⭐⭐ **2 — Medium** | Students who want the meaning word by word | **تفسير الجلالين** (al-Jalalayn) | Very compact, explains the words inside the verse itself. Short but dense. |
| ⭐⭐ **2 — Medium** | Readers who want the meaning with evidence | **تفسير ابن كثير** (Ibn Kathir) | Explains the Quran by the Quran and by hadith. The most widely read classical tafsir. |
| ⭐⭐⭐ **3 — Advanced** | Students of knowledge (طلاب العلم) | **تفسير البغوي** (al-Baghawi) | Collects the opinions of the early generations (السلف) with their narrations. |
| ⭐⭐⭐ **3 — Advanced** | Students interested in rulings (الأحكام) | **تفسير القرطبي** (al-Qurtubi) | Focused on the legal rulings derived from verses, with long juristic discussions. |
| ⭐⭐⭐⭐ **4 — Scholarly** | Researchers and specialists | **تفسير الطبري** (at-Tabari) | The foundational encyclopedia of tafsir. Full chains of narration, many opinions per verse, very long. |

### Why al-Muyassar is the favourite (المفضّل) for easy use

- **It's short.** A voice assistant can read it aloud in a few seconds. Reading at-Tabari aloud for one verse can take minutes.
- **It's clear.** Modern, simple Arabic — no technical terms to explain.
- **It's safe.** It gives the agreed-upon meaning, without listing weak or disputed opinions that confuse a beginner.

> **بالعربي:** التفسير الميسر هو الاختيار الأول للمستخدم العادي وللمساعد الصوتي: قصير وواضح، ويعطي المعنى المتفق عليه دون خلافات أو أسانيد. وإذا أراد المستخدم التعمق، يصعد درجة: السعدي ← ابن كثير ← القرطبي ← الطبري.

### How the levels are meant to be used

The ladder is meant to be **climbed**, not chosen once:

1. **Start easy.** Answer the user with level 1 (al-Muyassar / as-Sa'di).
2. **Go deeper on request.** If the user says "tell me more" (زدني), move to level 2 (Ibn Kathir / al-Jalalayn).
3. **Go scholarly only when asked.** Rulings → al-Qurtubi; full narrations and all opinions → at-Tabari.

> **Current status:** the difficulty level is returned with every result (the `difficulty` field) so the calling app can choose. The search itself does not yet filter or re-rank by difficulty — see the [Roadmap](#12-roadmap).

---

## 3. How a search works, step by step

```
 User question (Arabic)
   "ما تفسير قوله تعالى ولا يغتب بعضكم بعضا عند ابن كثير؟"
          │
          ▼
 ┌─────────────────────────────────────────────────────┐
 │ STEP 1 — Clean the question                        │
 │  • strip question words: "ما تفسير قوله تعالى"      │
 │  • strip book names at the end: "عند ابن كثير"      │
 │  • remove tashkeel (التشكيل)                        │
 │  → "ولا يغتب بعضكم بعضا"                            │
 └──────────────────────┬──────────────────────────────┘
                        ▼
 ┌─────────────────────────────────────────────────────┐
 │ STEP 2 — Find candidates (two fast searches)       │
 │  ① BM25 keyword search  → top 50 passages          │
 │  ② Verse-anchor search  → top 10 verses, and every  │
 │     passage that explains those verses              │
 │  Candidates = ① ∪ ②                                 │
 └──────────────────────┬──────────────────────────────┘
                        ▼
 ┌─────────────────────────────────────────────────────┐
 │ STEP 3 — Score every candidate on 3 signals        │
 │  BM25 (words)      × 0.50                           │
 │  Semantic (meaning)× 0.35                           │
 │  Anchor (verse)    × 0.15                           │
 │  Each signal is scaled to 0–1 before mixing.        │
 └──────────────────────┬──────────────────────────────┘
                        ▼
 ┌─────────────────────────────────────────────────────┐
 │ STEP 4 — Return the top K                          │
 │  text · verse key (49:12) · book · difficulty (1–4) │
 └─────────────────────────────────────────────────────┘
```

---

## 4. Every design idea, explained

### 4.1 Hybrid search — three signals instead of one

No single search method is good enough for classical Arabic text:

| Signal | Weight | What it catches | What it misses alone |
|---|:---:|---|---|
| **BM25** (keyword) — البحث بالكلمات | **50%** | Exact words, names, Quranic phrases. If you type part of a verse, BM25 finds it. | Synonyms. "العقوبة" won't match "الجزاء". |
| **Semantic** (meaning) — البحث بالمعنى | **35%** | Questions phrased differently from the book's wording. | Precise phrases; tends to return "related but vague" passages. |
| **Verse anchor** — مرساة الآية | **15%** | Pulls in passages from *every* book that explain the same verse. | Not enough alone to rank passages inside a verse. |

BM25 has the largest weight because tafsir questions very often quote the Quran directly, and exact wording is the strongest evidence.

> **بالعربي:** نجمع ثلاث طرق: البحث بالكلمات (أقوى إشارة، لأن الناس يقتبسون من القرآن مباشرة)، والبحث بالمعنى (إذا كُتب السؤال بكلمات مختلفة)، ومرساة الآية (لجلب كلام كل المفسرين على الآية نفسها).

### 4.2 Verse anchors — making the search "verse-aware"

Every ayah in the Quran (6,236 of them) has its own vector in a FAISS index (`faiss_anchor.index`). Every tafsir passage is linked to the verse(s) it explains through `anchor_dict` (`"49:12" → [row ids…]`).

When you search, the engine first finds the verses closest to your question, then boosts **all** tafsir passages linked to those verses. The result: if your question is about verse 49:12, you get Ibn Kathir *and* al-Qurtubi *and* as-Sa'di on 49:12 — not seven unrelated passages that happen to share a word.

### 4.3 Union optimization — fast without losing quality

Comparing the question against all ~24,000 passage embeddings on every request is slow on CPU. Instead, the semantic score is computed only for the **union of BM25's top 50 and the anchor-linked passages**. This keeps search fast while still letting meaning decide the final order among good candidates. (A `full_semantic=True` switch exists for testing against the whole corpus.)

### 4.4 Arabic-aware cleaning

Arabic text has features that break naive search. `utils.py` handles them:

| Problem | Example | Fix |
|---|---|---|
| Tashkeel (diacritics) | `الرَّحْمَنِ` vs `الرحمن` | Removed before matching |
| Different alef forms | `إ أ آ ا` | All → `ا` (for keyword search) |
| `ى/ي`, `ة/ه`, `ؤ/و`, `ئ/ي` | `هدى` vs `هدي` | Unified (for keyword search) |
| Conversational wrappers | `ما تفسير قوله تعالى…`, `ماذا قال المفسرون في…`, `شرح آية…` | Stripped, repeatedly, so layers like "تفسير آية" are peeled off |
| Book names inside the question | `…عند الطبري`, `…حسب ابن كثير` | Stripped so they don't pollute the search |

Note: for the **semantic** model only tashkeel is removed (letters stay as written), because full normalization can damage the meaning the model sees. Full normalization is used only for **BM25**.

### 4.5 Every result is traceable

Each result returns the **book name** and the **verse key** (e.g. `49:12`). Nothing is generated or paraphrased: the text is the scholar's own words. This matters for religious content — the user (or the voice agent) can always say *who said it* and *about which verse*.

> **بالعربي:** المحرك لا يؤلف كلاماً. كل نتيجة هي نص المفسر نفسه، ومعها اسم الكتاب ورقم الآية، فالمصدر واضح دائماً.

### 4.6 Built for voice, not only for screens

- Error messages are written **fully diacritized** (`عَفْواً، السُّؤَالُ فَارِغٌ.`) so a text-to-speech model pronounces them correctly.
- The search function `get_tafsir(query, top_k)` is async and returns plain JSON, so it plugs directly into an agent as a tool.

### 4.7 Fast cold start

- The embedding model is **downloaded at Docker build time**, so the first request doesn't wait for a download.
- All indexes (BM25, FAISS, embeddings) are **precomputed** and loaded once at startup.
- Query embeddings are **cached** in memory (1,024 entries), so repeated questions skip the model entirely.

---

## 5. The data

All files live in `data/` and are stored with **Git LFS**.

| File | What it is |
|---|---|
| `tafsir.csv` | The corpus. Columns: `resource_name` (book), `verses_keys` (e.g. `"100:1,100:2"` — one passage can cover several verses), `text` (the passage). |
| `tafsir_embeddings.npy` | One 384-dim vector per passage (23,746 passages). |
| `bm25.pkl` | Prebuilt BM25 index over the normalized passages. |
| `faiss_anchor.index` | One vector per ayah (6,236). |
| `anchor_dict.pkl` | `verse_key → [passage row ids]` |
| `unique_anchor_texts.pkl` | Verse keys, in the same order as the FAISS index. |

Embedding model: [`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) (384 dims).

> To clone with the data: `git lfs install` before `git clone`. Without LFS you get small pointer files instead of the data.

---

## 6. API

### `POST /api/search`

**Request**
```json
{ "query": "حكم الغيبة وعقوبتها", "top_k": 5 }
```
`top_k`: 1–10 in the web UI.

**Response**
```json
{
  "results": [
    {
      "rank": 1,
      "text": "…نص المفسر…",
      "verses_keys": "49:12",
      "resource_name": "تفسير ابن كثير",
      "difficulty": 2
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `rank` | Position after hybrid scoring (1 = best) |
| `text` | The scholar's passage, unmodified |
| `verses_keys` | Verse(s) explained, `surah:ayah`, comma-separated |
| `resource_name` | Tafsir book |
| `difficulty` | 1 easy · 2 medium · 3 advanced · 4 scholarly ([table](#2-the-difficulty-ladder--who-each-tafsir-is-for)) |

**curl**
```bash
curl -X POST http://localhost:7860/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "الصبر على البلاء", "top_k": 3}'
```

---

## 7. Using it as a tool for a voice agent (MCP)

`tafsir_mcp.py` exposes the search as a plain async function:

```python
from tafsir_mcp import get_tafsir

result = await get_tafsir("ما معنى الصبر الجميل", top_k=3)
# {"tafsir_chunks": [ {rank, text, verses_keys, resource_name, difficulty}, … ],
#  "error": None}
```

Recommended agent behaviour (this is how it's used in **Muslim**):

1. Call `get_tafsir` with the user's question.
2. Prefer the **level 1** result (al-Muyassar / as-Sa'di) for the spoken answer.
3. Always say the **book name** and the **verse**.
4. If the user asks for more, read the level 2–3 results.

---

## 8. Run it yourself

**Locally**
```bash
git lfs install
git clone https://github.com/NightPrinceY/Tafsir_Search
cd Tafsir_Search
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
# open http://localhost:7860
```

**Docker**
```bash
docker build -t tafsir-search .
docker run -p 7860:7860 tafsir-search
```

Requirements: `fastapi`, `uvicorn`, `pandas`, `numpy`, `faiss-cpu`, `rank-bm25`, `sentence-transformers`, `cachetools`, `python-dotenv`. CPU only — no GPU needed.

---

## 9. Project structure

```
├── app.py            # FastAPI: POST /api/search + serves the web UI
├── tafsir_mcp.py     # get_tafsir(): loads indexes once, runs the search, formats results,
│                     #   holds the difficulty mapping
├── retrieval.py      # hybrid_search_fixed(): BM25 + semantic + anchor, union optimization
├── hf_model.py       # Thread-safe SentenceTransformer wrapper + embedding cache
├── utils.py          # Arabic cleaning: tashkeel, letter normalization, question-prefix stripping
├── index.html        # RTL Arabic web UI
├── assets/           # script.js (fetch + render cards), style.css
├── data/             # corpus + precomputed indexes (Git LFS)
└── Dockerfile        # python:3.10-slim, model baked in at build time
```

---

## 10. The family of engines this belongs to

All built by the same author, for the **Muslim** voice AI companion:

| Engine | Question it answers | Link |
|---|---|---|
| **Tafsir Search** (this repo) | *"What did the scholars say about X?"* → tafsir passages | — |
| **Quran Semantic Retrieval** | *"Which verse talks about X?"* → the ayah itself. Uses this same tafsir index: **the tafsir is the search index, the ayah is the answer.** | [GitHub](https://github.com/NightPrinceY/Quran-Semantic-Retrieval) · [Space](https://huggingface.co/spaces/NightPrince/Quran-Semantic-Retrieval) |
| **Hadith Search** | Same hybrid architecture over hadith | [GitHub](https://github.com/NightPrinceY/Hadith_Search) |
| **Islamic MCP Server** | *"Give me the tafsir of 2:255"* → direct lookup by verse number from 8 books, plus recitation audio | [GitHub](https://github.com/NightPrinceY/islamic-mcp-server) |

**Search vs. lookup:** use **this engine** when you have a *question*; use the **Islamic MCP Server** when you already know the *verse number*.

---

## 11. Known limitations

Stated plainly, so you know what to expect:

- **General embedding model.** `paraphrase-multilingual-MiniLM-L12` is multilingual, not specialized for classical Arabic. Meaning-based matching on old scholarly Arabic is the weakest of the three signals.
- **Semantic search only on candidates.** If a question shares no words with the right passage *and* the anchor misses the right verse, the right passage never gets a semantic score.
- **Difficulty is a label, not a filter.** You get the level with every result, but you can't yet ask for "level 1 only".
- **Long passages.** Some passages (especially at-Tabari and al-Qurtubi) are very long; they are returned whole.
- **Arabic only.** Queries and tafsir are Arabic.

---

## 12. Roadmap

- [ ] `max_difficulty` / `books` parameter — search only the levels the user wants
- [ ] Difficulty-aware ranking — prefer easier books when scores are close
- [ ] Arabic-specialized embedding model, evaluated on a labelled set of tafsir questions
- [ ] Passage chunking for very long passages
- [ ] Unify the book list with the Islamic MCP Server (al-Wasit, Tanwir al-Miqbas)

---

## Built by

**يحيى النوساني — Yahya Elnawasany** · [Hugging Face](https://huggingface.co/NightPrince) · [GitHub](https://github.com/NightPrinceY)

# Chelsea FC Intelligence Hub — RAG App

A Retrieval-Augmented Generation (RAG) application that lets you ask questions about Chelsea Football Club using a locally-built vector search pipeline powered by Google Gemini.

---

## What document did you use and why?

A custom-authored PDF (`chelsea_fc.pdf`) covering the full history of Chelsea FC — founding in 1905, the first league title in 1955, the Abramovich revolution, iconic players (Drogba, Terry, Lampard, Hazard), all trophy wins, and the current Boehly era. Chelsea FC was chosen because the structured, fact-dense nature of football history is ideal for RAG: questions have specific, verifiable answers that map cleanly to text chunks.

---

## How does your chunking work?

Fixed-size word chunking with overlap (`utils/loader.py`):

- Each chunk is **400 words** long.
- Chunks overlap by **60 words** to prevent context from being cut at boundaries (e.g. a sentence about a player's goal tally doesn't get split in half).
- The step size is `400 - 60 = 340 words`, so consecutive chunks share a 60-word tail/head.

This keeps chunks large enough to contain complete facts while the overlap preserves coherence across boundaries.

---

## Which embedding model did you use?

**`all-MiniLM-L6-v2`** from `sentence-transformers`.

- Runs entirely locally — no API key, no cost.
- 384-dimensional embeddings; fast on CPU.
- Strong semantic similarity performance for factual question-answering tasks.
- Vectors stored in a **FAISS `IndexFlatL2`** index for exact nearest-neighbour search.

---

## How to run locally

### Prerequisites
- Python 3.11+
- A Google Gemini API key (free tier available at [aistudio.google.com](https://aistudio.google.com))

### Steps

```bash
# 1. Clone the repo and enter the folder
git clone <your-repo-url>
cd your-name-rag-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate the Chelsea FC PDF (only needed once)
python data/create_pdf.py

# 4. Create your .env file
echo GEMINI_API_KEY=your_key_here > .env

# 5. Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`.

> **Note:** The first run downloads the `all-MiniLM-L6-v2` model (~90 MB). Subsequent runs use the cached version.

---

## Screenshot

<img width="1915" height="986" alt="loading_page" src="https://github.com/user-attachments/assets/0c1aa4c7-f666-4efe-bff4-a461f3937c21" />

---

## What would you improve with more time?

1. **Semantic / recursive chunking** — split on paragraph or sentence boundaries rather than fixed word counts for more coherent chunks.
2. **Hybrid retrieval** — combine dense vector search (FAISS) with sparse BM25 keyword search; better for specific names and dates.
3. **Conversation memory** — pass prior Q&A turns as context so follow-up questions like "what did he win?" work correctly.
4. **Metadata filtering** — tag each chunk with its era (e.g. "1905–1939") so the retriever can scope searches by time period.
5. **Streaming PDF upload** — let users upload their own documents at runtime instead of a hardcoded file.
6. **Re-ranking** — add a cross-encoder re-ranker pass after retrieval to improve chunk relevance ordering.

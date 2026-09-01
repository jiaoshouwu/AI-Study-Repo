# Day 8 - Persistent RAG State

## Goal

Persist the RAG embedding index so that
unchanged documents do not need to be
embedded again every time the program starts.

## Architecture

README
→ Chunk
→ Signature

Startup
→ Check Persistent Index

Fresh
→ Load Index

Missing / Stale
→ Generate Embeddings
→ Save Index

Question
→ Query Embedding
→ Semantic Search
→ RAG Answer

## What I Learned

1. State can survive beyond one process run.
2. Embeddings are expensive computed state.
3. Cached embeddings can be reused.
4. Persisted state needs freshness checking.
5. A source signature can detect stale state.
6. Changing the embedding model invalidates
   the old vector index.
7. Query embedding is still required even
   when document embeddings are cached.

## Tests

- [x] cold start creates persistent index
- [x] warm start reuses persistent index
- [x] stale index triggers rebuild
- [x] grounded RAG behavior still works

## Observation

State and memory are related but different:

State stores application data needed to
continue operating.

Memory stores information that an agent may
use later to influence its decisions.
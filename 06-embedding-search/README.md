# Day 6 - Embedding and Semantic Search

## Goal

Convert my previous learning notes into
embeddings and retrieve relevant chunks
using semantic similarity.

## Architecture

README files
→ Chunking
→ Embeddings
→ Vector Index

Question
→ Query Embedding
→ Cosine Similarity
→ Top-K Chunks

## What I Learned

1. Embeddings represent text as vectors.
2. Embeddings do not generate answers.
3. Chunking determines the retrieval unit.
4. Semantic search can match meaning
   without exact keywords.
5. Cosine similarity compares vectors.
6. Top-K retrieval selects the most
   relevant context.
7. A Python list can act as a tiny
   vector store for learning purposes.

## Tests

- [ ] tool-calling question retrieves Day 2
- [ ] agent-loop question retrieves Day 3/5
- [ ] planning question retrieves Day 4
- [ ] evidence question retrieves Day 5

## Question for next day

How can retrieved chunks be supplied to
an LLM so that it answers using only the
retrieved knowledge?
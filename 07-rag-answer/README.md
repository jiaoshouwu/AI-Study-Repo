# Day 7 - First RAG System

## Goal

Retrieve relevant learning notes and
use them as context for an LLM answer.

## Architecture

Question
→ Query Embedding
→ Semantic Search
→ Top-K Chunks
→ Build Context
→ LLM
→ Grounded Answer
→ Sources

## What I Learned

1. Retrieval finds relevant information.

2. Augmentation puts retrieved information
   into the LLM context.

3. Generation converts context into
   a natural-language answer.

4. Embeddings do not answer questions.

5. Retrieval quality and generation quality
   are separate problems.

6. A grounded model should refuse to answer
   when retrieved context is insufficient.

7. Sources should travel from retrieval
   into the final answer.

## Tests

- [x] tool calling question
- [x] agent loop question
- [x] research planning question
- [x] unknown question refuses to invent

## Question for next day

How can I persist the embeddings instead
of rebuilding the whole index every time
the program starts?

## Observation

My first RAG test failed even though the
embedding search returned a high similarity
score.

The query:

"How can an LLM call a Python function?"

matched a "Question for tomorrow" section
from Day 1 instead of the actual answer
from Day 2.

This showed me that:

1. High similarity does not guarantee
   useful evidence.

2. Chunk quality matters.

3. Questions and metadata should not always
   be indexed as knowledge.

4. RAG debugging should inspect retrieved
   chunks before changing the LLM prompt.

5. Retrieval failure and generation failure
   are different problems.
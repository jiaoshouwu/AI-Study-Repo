# Day 17 - Multi-Agent Supervisor

## Goal

Build a minimal multi-agent system with
one supervisor and two specialized workers.

## Architecture

User
→ Supervisor
  ├→ Researcher → END
  └→ Coder      → END

## Agents

### Supervisor

Responsibilities:
- understand the request
- select a specialist
- do not answer the task

### Researcher

Responsibilities:
- factual research
- current information
- source-based answers

Tools:
- web_search

### Coder

Responsibilities:
- coding
- debugging
- implementation explanation

Tools:
- none

## What I Learned

1. A model is not the same as an agent.
2. Multiple agents can share one model.
3. Agents can differ by instructions,
   tools and execution policy.
4. The supervisor delegates work.
5. Tool access should follow least privilege.
6. LLM routing output must be validated.
7. Shared graph state records handoffs.

## Tests

- [x] coding request routes to coder
- [x] debugging request routes to coder
- [x] research request routes to researcher
- [x] empty request is rejected

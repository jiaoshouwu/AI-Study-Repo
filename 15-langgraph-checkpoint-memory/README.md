# Day 15 - LangGraph Checkpoint and Thread Memory

## Goal

Use a LangGraph checkpointer to preserve graph
state across multiple invocations in the same
thread.

## Architecture

thread_id
   ↓
Checkpointer
   ↓
START
→ remember
→ answer
→ END

## What I Learned

1. A checkpoint is a snapshot of graph state.

2. A checkpointer saves and restores graph state.

3. thread_id identifies an independent
   conversation.

4. Reusing the same thread_id restores previous
   state.

5. Different thread IDs have isolated state.

6. graph.get_state() reads the latest checkpoint.

7. InMemorySaver survives multiple invoke()
   calls but not process restart.

8. LangGraph checkpointing replaces manual
   state save/load logic for graph workflows.

## Tests

- [x] same thread remembers previous state
- [x] different threads have isolated state
- [x] switching back restores previous state
- [x] process restart clears InMemorySaver

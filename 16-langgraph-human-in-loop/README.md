# Day 16 - LangGraph Human in the Loop

## Goal

Pause a LangGraph workflow for structured
human approval before executing an action.

## Architecture

START
→ plan
→ review
→ interrupt
  ├→ approve → execute → END
  └→ reject  → cancel  → END

## What I Learned

1. interrupt() pauses graph execution.
2. A checkpointer preserves interrupted state.
3. thread_id identifies the workflow to resume.
4. Command(resume=...) returns external input
   to interrupt().
5. Resume values can be structured data.
6. Command(update=...) updates graph state.
7. Command(goto=...) controls routing.
8. The interrupted node restarts from its
   beginning when resumed.
9. Side effects should happen after approval
   or must be idempotent.
10. Human review can store an audit reason.

## Tests

- [x] approve reaches execute
- [x] reject reaches cancel
- [x] graph is pending before resume
- [x] graph reaches END after resume

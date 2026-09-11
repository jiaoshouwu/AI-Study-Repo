# Day 14 - LangGraph Loop and Bounded Retry

## Goal

Build a LangGraph workflow that evaluates
an answer, revises it when necessary, and
loops back for another evaluation.

## Architecture

START
→ draft
→ evaluate
  ├→ finish → END
  └→ revise
       ↓
     evaluate

## State

AgentState contains:

- question
- answer
- attempt
- quality_ok
- decision
- status
- trace

## What I Learned

1. A graph can contain cycles.

2. An edge can point back to an earlier node.

3. Conditional edges can decide whether to
   continue a loop or exit it.

4. Every agent loop needs a clear exit
   condition.

5. MAX_ATTEMPTS provides an application-level
   bounded retry.

6. recursion_limit provides a framework-level
   safety guard.

7. Evaluation and routing should have separate
   responsibilities.

8. A previous answer can be stored in state and
   reused by a revise node.

## Tests

- [x] failed first draft triggers revise
- [x] passing evaluation skips revise
- [x] loop stops at MAX_ATTEMPTS
- [x] empty input does not execute graph

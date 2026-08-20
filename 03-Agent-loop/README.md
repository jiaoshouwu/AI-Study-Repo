# Day 3 - Agent Loop

## Goal

Build an Agent that can repeatedly call
tools until the task is complete.

## Flow

User
→ LLM
→ Tool Call
→ Python Tool
→ Tool Result
→ LLM
→ ...
→ Final Answer

## Key Difference

Day 2:

LLM
→ Tool
→ LLM
→ End

Day 3:

while task is not complete:
    LLM
    → Tool
    → Observation

## What I Learned

1. Tool Calling alone is not an Agent Loop.
2. The LLM decides the next action.
3. Python executes and controls the loop.
4. Tool results become new context.
5. The loop stops when there are no tool calls.
6. MAX_STEPS prevents runaway loops.
7. A tool error can become an observation instead of crashing the agent.
8. The output of one tool can become the input of another tool in a later step.

## Tests

- [x] no-tool question
- [x] single tool call
- [x] sequential tool calls
- [x] tool error

## Question for next day

How can an Agent reason about what step to take before choosing a tool?


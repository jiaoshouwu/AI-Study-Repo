# Day 11 - Structured Agent State

## Goal

Represent all important agent runtime information
inside one structured state object.

## Architecture

START
→ create_state
→ prepare_node
→ answer_node
→ finish_node
→ END

Each node receives AgentState and returns AgentState.

## State

AgentState contains:

- question
- answer
- step
- status

## What I Learned

1. Agent state represents the current runtime
   information of an agent.

2. Nodes read and update state.

3. A workflow is a sequence of state transitions.

4. TypedDict gives the state an explicit schema.

5. Pylance can detect incorrect state field types.

6. LLM input can come from state and LLM output
   can be written back into state.

7. This state → node → state pattern prepares
   the code for graph-based agent frameworks.

## Tests

- [x] nodes execute in correct order
- [x] question and answer travel through state
- [x] empty question does not call the model
- [x] AgentState type errors are detected

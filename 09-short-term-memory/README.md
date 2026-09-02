# Day 9 - Short-Term Conversation Memory

## Goal

Give an LLM multi-turn conversation memory
by keeping previous user and assistant messages
in application state.

## Architecture

User Message
→ Conversation History
→ LLM
→ Assistant Answer
→ Append User + Assistant Messages
→ Conversation History
→ Next Turn

## What I Learned

1. An LLM does not automatically remember
   previous independent API calls.

2. Conversation memory can be stored by
   the application.

3. Previous messages must be included in
   the next model request.

4. The model appears to remember because
   the relevant history is provided as context.

5. Short-term memory disappears when the
   process exits.

6. Clearing application history clears the
   agent's conversation memory.

7. Memory and model instructions are
   different concepts.

## Commands

- /history - inspect conversation memory
- /reset - clear conversation memory
- /exit - exit the program

## Tests

- [x] model recalls a fact from an earlier turn
- [x] model recalls multiple-turn context
- [x] /reset clears conversation memory
- [x] process restart loses short-term memory

## Observation

The model itself is not storing my conversation
inside this Python application.

The application stores the messages and sends
them back to the model on later turns.

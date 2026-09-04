# Day 10 - Persistent Conversation Memory

## Goal

Persist conversation memory outside the Python
process and restore it after restart.

## Architecture

Conversation History
→ Serialize
→ JSON File

Restart

JSON File
→ Deserialize
→ Conversation History
→ LLM

## What I Learned

1. Runtime memory disappears when a process exits.
2. Persistent memory is stored outside the process.
3. Serialization converts Python state to storage.
4. Deserialization restores stored state.
5. The LLM itself still does not retain this memory.
6. The application reloads history and injects it
   into later model requests.
7. Persistent state should be validated before use.
8. Reset must clear both RAM and persistent storage.

## Tests

- [x] first run creates persistent memory
- [x] restart restores memory
- [x] /reset removes persistent memory
- [x] invalid JSON does not crash the program

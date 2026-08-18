# Day 1 - Minimal LLM Call

## Goal

Make a minimal LLM API call without using any agent framework.

## What I built

Input
→ Python
→ OpenAI API
→ LLM
→ Response

## What I learned

1. An LLM call is not an Agent.
2. My Python program currently controls when the LLM is called.
3. The model receives input and returns generated output.
4. The LLM currently cannot execute external tools.
5. API keys should not be stored in source code.

## Tests

- [x] Simple prompt
- [x] Chinese prompt
- [x] Translation prompt
- [x] Empty prompt validation

## Question for tomorrow

How can an LLM decide to call a Python function?
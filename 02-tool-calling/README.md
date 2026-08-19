# Day 2 - Tool Calling

## Goal

Allow an LLM to decide when to call a Python calculator tool.

## Flow

User
→ LLM
→ Function Call
→ Python Tool
→ Function Result
→ LLM
→ Final Answer

## What I learned

1. A tool definition describes a Python capability to the LLM.
2. The LLM chooses which tool to call.
3. The LLM does not execute the Python function itself.
4. Python parses tool arguments and executes the function.
5. The tool result must be sent back to the LLM.
6. A normal question should not trigger the calculator.

## Tests

- [ ] multiplication
- [ ] division
- [ ] normal conversation without tool
- [ ] divide by zero

## Question for next day

What happens when an Agent needs to call tools repeatedly?
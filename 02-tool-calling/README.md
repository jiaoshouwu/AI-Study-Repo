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

- [x] multiplication
- [x] division
- [x] normal conversation without tool
- [x] divide by zero

## Question for next day

What happens when an Agent needs to call tools repeatedly?


### observation
if I change the description of tool to inacurate sentence, such as "A useful funciton" , the tool will not be called anymore. 
so Tool description matters. 


when I did the test "divide by zero", the tool is not called as expected,even after I changed the "return ValueError" in main.py to "raise ValueError"

import json
import os

from openai import OpenAI

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")


def calculator(a: float, b: float, operation: str) -> float:
    if operation == "add":
        return a + b

    if operation == "subtract":
        return a - b

    if operation == "multiply":
        return a * b

    if operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")

        return a / b

    raise ValueError(f"Unknown operation: {operation}")


calculator_tool = {
    "type": "function",
    "name": "calculator",
    "description": (
        # "a useful function."
        "Perform basic arithmetic operations."
        "Use this tool when exact arithmetic is required."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "the first number",
            },
            "b": {
                "type": "number",
                "description": "the second number",
            },
            "operation": {
                "type": "string",
                "enum": [
                    "add",
                    "subtract",
                    "multiply",
                    "divide",
                ],
                "description": "the operation to perform",
            },
        },
        "required": [
            "a",
            "b",
            "operation",
        ],
        "additionalProperties": False,
    },
    "strict": True,
}


def get_secret_number() -> int:
    return 42


secret_number_tool = {
    "type": "function",
    "name": "get_secret_number",
    "description": (
        "Returns a secret number.Use this tool when you need a secret number."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
        "additionalProperties": False,
    },
}

TOOLS = [calculator_tool, secret_number_tool]


def execute_tool(tool_name: str, arguments: dict) -> str:
    if tool_name == "calculator":
        result = calculator(
            a=arguments["a"],
            b=arguments["b"],
            operation=arguments["operation"],
        )
        return str(result)

    if tool_name == "get_secret_number":
        return str(get_secret_number())

    raise ValueError(f"Unknown tool: {tool_name}")


MAX_STEPS = 8

trace = []


def run_agent(user_input: str) -> str:

    input_items = [
        {
            "role": "user",
            "content": user_input,
        }
    ]

    for step in range(1, MAX_STEPS + 1):
        print(f"\n --- Step {step} ---")

        response = client.responses.create(
            model=MODEL,
            input=input_items,
            tools=TOOLS,
            tool_choice="auto",
        )

        input_items += response.output

        tool_calls = [item for item in response.output if item.type == "function_call"]

        if not tool_calls:
            return response.output_text

        for tool_call in tool_calls:
            # print(f"Tool: {tool_call.name}")

            # print(f"Arguments: {tool_call.arguments}")

            arguements = json.loads(tool_call.arguments)

            try:
                result = execute_tool(tool_call.name, arguements)
            except Exception as error:
                result = f"Error: {error}"
                print(f"Tool error: {result}")

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result,
                }
            )

            trace.append(
                {
                    "step": step,
                    "tool": tool_call.name,
                    "arguments": arguements,
                    "result": result,
                }
            )

    return f"Agent stopped because MAX_STEPS:{MAX_STEPS} reached."


if __name__ == "__main__":
    user_input = input("You: ")

    answer = run_agent(user_input)

    print(f"\nAgent: {answer}")

    print("\nAgent Trace:")
    for item in trace:
        print(
            f"Step {item['step']}:"
            f" {item['tool']}({item['arguments']}) = {item['result']}"
        )

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
            return ValueError("Cannot divide by zero")


        return a / b

    raise ValueError(f"Unknown operation: {operation}")

TOOLS = [
    {
        "type": "function",
        "name": "calculator",
        "description": (
            #"a useful function."
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
        "strict" : True,
    }
]

def ask_with_tools(user_input: str) -> str:
    input_items = [
        {
            "role": "user",
            "content": user_input,
        }
    ]

    response = client.responses.create(
        model=MODEL,
        input=input_items,
        tools=TOOLS,
        tool_choice="auto",
    )

    input_items += response.output

    tool_was_called = False

    for item in response.output:
        if item.type != "function_call":
            continue

        tool_was_called = True

        print(f"\nTool called: {item.name}")
        print(f"Arguements: {item.arguments}")

        if item.name == "calculator":
            args = json.loads(item.arguments)
            try: 
                result = calculator(
                    a=args["a"],
                    b=args["b"],
                    operation=args["operation"],
                )
            except ValueError as error:
                result = f"Error: {error}"
                
            print(f"Tool result: {result}")

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": str(result),
                }
            )

    if not tool_was_called:
        return response.output_text

    final_response = client.responses.create(
        model=MODEL,
        input=input_items,
        tools=TOOLS,
    )
    return final_response.output_text


if __name__ == "__main__":
    #print(calculator(23,87,"multiply"))
    user_input = input("You: ")

    answer = ask_with_tools(user_input)

    print(f"\n AI: {answer}")
import os

from openai import OpenAI

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6")

def ask_llm(prompt: str) -> str: 
    """send a prompt to an LLM and return its text response"""

    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    response = client.responses.create(
            model = MODEL,
            input = prompt,
    )

    return response.output_text


if __name__ == "__main__":
    user_input = input("You: ")


    answer = ask_llm(user_input)
    

    print(f"\n AI: {answer}")



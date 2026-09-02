import os

from openai import OpenAI

client = OpenAI()

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
)

MAX_MESSAGES = 6

ChatMessage = dict[str, str]  # type alias for chat messages

INSTRUCTIONS = """
You are a concise AI learning assistant.

Use the conversation history when answering.

if the user asks aboout something they told you earlier,
use that information when appropriate.
""".strip()


def chat_turn(
    user_text: str,
    history: list[ChatMessage],
) -> str:

    messages = history.copy()

    messages.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    response = client.responses.create(
        model=MODEL,
        instructions=INSTRUCTIONS,
        input=messages,
    )

    answer = response.output_text

    history.append(
        {
            "role": "user",
            "content": user_text,
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    trim_history(history)

    return answer


def print_history(history: list[ChatMessage]) -> None:
    print("\n=== Conversation Memory: ==")

    if not history:
        print("(empty)")

    for index, message in enumerate(
        history,
        start=1,
    ):
        role = message["role"]
        content = message["content"]

        print(f"{index}. {role.capitalize()}: {content}")


def run_chat() -> None:

    history: list[ChatMessage] = []

    print("Short-term memory Chat\n")
    print("Commands: /history,/reset, /exit\n")

    while True:
        user_text = input("\nYou: ").strip()

        if not user_text:
            continue

        if user_text == "/exit":
            break

        if user_text == "/reset":
            history.clear()
            print(" memory cleared.\n")
            continue

        if user_text == "/history":
            print_history(history)
            continue

        answer = chat_turn(
            user_text,
            history,
        )

        print(f"\nAI: {answer}\n")


def trim_history(
    history: list[ChatMessage],
) -> None:

    if len(history) > MAX_MESSAGES:
        del history[:-MAX_MESSAGES]


if __name__ == "__main__":
    run_chat()

import json
import os
from pathlib import Path

from openai import OpenAI

APP_DIR = Path(__file__).resolve().parent
MEMORY_FILE = APP_DIR / "data" / "conversation.json"

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

    history = load_history()

    print("Short-term memory Chat\n")
    print("Commands: /history,/reset, /exit\n")

    while True:
        user_text = input("\nYou: ").strip()

        if not user_text:
            continue

        if user_text == "/exit":
            break

        if user_text == "/reset":
            clear_history(history)
            print("Persistent Memory cleared.\n")
            continue

        if user_text == "/history":
            print_history(history)
            continue

        answer = chat_turn(
            user_text,
            history,
        )

        save_history(history)

        print(f"\nAI: {answer}\n")


def trim_history(
    history: list[ChatMessage],
) -> None:

    if len(history) > MAX_MESSAGES:
        del history[:-MAX_MESSAGES]


def load_history() -> list[ChatMessage]:
    if not MEMORY_FILE.exists():
        print("No persistent conversation found.")
        return []

    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    except (
        json.JSONDecodeError,
        OSError,
    ):
        print("Invalid persistent memory.Starting with empty history")
        return []

    if not isinstance(data, list):
        print("Persistent memory has an invalid format.")
        return []

    history: list[ChatMessage] = []

    for item in data:
        if not isinstance(item, dict):
            continue

        role = item.get("role")
        content = item.get("content")

        if role not in {
            "user",
            "assistant",
        }:
            continue

        if not isinstance(content, str):
            continue

        history.append(
            {
                "role": role,
                "content": content,
            }
        )

    return history[-MAX_MESSAGES:]


def save_history(
    history: list[ChatMessage],
) -> None:
    MEMORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        MEMORY_FILE.write_text(
            json.dumps(
                history,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError as e:
        print(f"Failed to save conversation history: {e}")


def clear_history(
    history: list[ChatMessage],
) -> None:
    history.clear()

    if MEMORY_FILE.exists():
        try:
            MEMORY_FILE.unlink()
            print("Persistent memory cleared.")
        except OSError as e:
            print(f"Failed to clear persistent memory: {e}")
    else:
        print("No persistent memory to clear.")


if __name__ == "__main__":
    run_chat()

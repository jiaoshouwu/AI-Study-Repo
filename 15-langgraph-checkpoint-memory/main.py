import os
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from openai import OpenAI

client = OpenAI()

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
)


class AgentState(TypedDict, total=False):
    message: str
    history: list[str]
    turn_count: int
    last_answer: str


def remember_node(
    state: AgentState,
) -> dict:
    message = state["message"]

    turn_count = state.get("turn_count", 0) + 1

    history = state.get("history", []) + [f"user: {message}"]

    print(f"Remember turn {turn_count}")

    return {
        "turn_count": turn_count,
        "history": history,
    }


def answer_node(
    state: AgentState,
) -> dict:
    transcript = "\n".join(
        state.get(
            "history",
            [],
        )
    )

    response = client.responses.create(
        model=MODEL,
        instructions=(
            "You are a concise AI engineering "
            "learning assistant. "
            "When asked about a user fact or "
            "preference, use only facts that "
            "appear in the saved conversation. "
            "If the fact is not present, say "
            "that you do not know."
        ),
        input=(f"Saved conversation:\n{transcript}\n\nAnswer the latest user message"),
    )

    answer = response.output_text

    history = state["history"] + [f"assistant: {answer}"]

    return {
        "last_answer": answer,
        "history": history,
    }


def build_graph() -> CompiledStateGraph:
    builder = StateGraph(
        AgentState,
    )

    builder.add_node(
        "remember",
        remember_node,
    )

    builder.add_node(
        "answer",
        answer_node,
    )

    builder.add_edge(
        START,
        "remember",
    )

    builder.add_edge(
        "remember",
        "answer",
    )

    builder.add_edge(
        "answer",
        END,
    )

    checkpointer = InMemorySaver()

    return builder.compile(
        checkpointer=checkpointer,
    )


def make_config(
    thread_id: str,
) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def run_turn(
    graph: CompiledStateGraph,
    thread_id: str,
    message: str,
) -> AgentState:
    return graph.invoke(
        {
            "message": message,
        },
        make_config(thread_id),
    )


def show_state(graph: CompiledStateGraph, thread_id: str) -> None:
    snapshot = graph.get_state(make_config(thread_id))

    state = snapshot.values

    print(f"Thread: {thread_id}")

    print(
        "Turn count:",
        state.get(
            "Turn_count",
            0,
        ),
    )

    print("History:")

    for item in state.get(
        "history",
        [],
    ):
        print(f" {item}")


def main() -> None:
    graph = build_graph()

    thread_id = "alpha"

    print("Commands:")

    print(" /thread <id>")

    print(" /state")

    print(" /exit")

    while True:
        text = input(f"\n[{thread_id}] You: ").strip()

        if not text:
            continue

        if text == "/exit":
            break

        if text == "/state":
            show_state(
                graph,
                thread_id,
            )
            continue

        if text.startswith("/thread"):
            new_thread = text.split(maxsplit=1)[1].strip()

            if new_thread:
                thread_id = new_thread

                print(f"switch to thread: {thread_id}")

                continue

        state = run_turn(
            graph,
            thread_id,
            text,
        )

        print(
            "\nAssistant:",
            state["last_answer"],
        )


if __name__ == "__main__":
    main()

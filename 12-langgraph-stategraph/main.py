import os
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from openai import OpenAI

client = OpenAI()
MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
)


class AgentState(TypedDict):
    question: str
    answer: str
    step: int
    status: Literal[
        "new",
        "prepared",
        "answered",
        "finished",
    ]
    trace: list[str]


def prepare_node(
    state: AgentState,
) -> dict:
    step = state["step"] + 1

    print(f"Step {step}: prepare")

    return {
        "step": step,
        "status": "prepared",
        "trace": state["trace"] + ["prepare"],
    }


def answer_node(
    state: AgentState,
) -> dict:
    step = state["step"] + 1

    print(f"Step {step}: answer")

    response = client.responses.create(
        model=MODEL,
        instructions=("You are a concise AI engineering learning assistant."),
        input=state["question"],
    )

    return {
        "answer": response.output_text,
        "step": step,
        "status": "answered",
        "trace": state["trace"] + ["answer"],
    }


def finish_node(
    state: AgentState,
) -> dict:
    step = state["step"] + 1

    print(f"Step {step}: finish")

    return {
        "step": step,
        "status": "finished",
        "trace": state["trace"] + ["finish"],
    }


def build_graph():
    builder = StateGraph(
        AgentState,
    )

    builder.add_node(
        "prepare",
        prepare_node,
    )
    builder.add_node(
        "answer",
        answer_node,
    )
    builder.add_node(
        "finish",
        finish_node,
    )

    builder.add_edge(
        START,
        "prepare",
    )

    builder.add_edge(
        "prepare",
        "answer",
    )

    builder.add_edge(
        "answer",
        "finish",
    )

    builder.add_edge(
        "finish",
        END,
    )
    return builder.compile()


def run_agent(
    question: str,
) -> AgentState:
    graph = build_graph()

    print(graph.get_graph().draw_mermaid())

    initial_state: AgentState = {
        "question": question,
        "answer": "",
        "step": 0,
        "status": "new",
        "trace": [],
    }

    result = graph.invoke(initial_state)

    return result


def main() -> None:
    question = input("Question: ").strip()
    if not question:
        print("Question cannot be empty")
        return

    state = run_agent(question)

    print("\n=== Final State: ===")
    print(f"Status: {state['status']}")
    print(f"Steps: {state['step']}")

    print("Trace: " + " -> ".join(state["trace"]))

    print(f"Answer: {state['answer']}")


if __name__ == "__main__":
    main()

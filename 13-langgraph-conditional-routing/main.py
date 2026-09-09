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
        "classified",
        "answered",
        "finished",
    ]

    route: Literal[
        "unclassified",
        "simple",
        "complex",
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


def concise_answer_node(
    state: AgentState,
) -> dict:
    step = state["step"] + 1

    print(f"Step {step}: concise_answer")

    response = client.responses.create(
        model=MODEL,
        instructions=("Answer the question concisely in 2 or 3 sentences."),
        input=state["question"],
    )

    return {
        "answer": response.output_text,
        "step": step,
        "status": "answered",
        "trace": state["trace"] + ["concise_answer"],
    }


def detailed_answer_node(
    state: AgentState,
) -> dict:
    step = state["step"] + 1

    print(f"Step {step}: detailed_answer")

    response = client.responses.create(
        model=MODEL,
        instructions=(
            "Answer as an AI engineering "
            "assistant. Give a structured "
            "technical explanation with "
            "key trade-off"
        ),
        input=state["question"],
    )

    return {
        "answer": response.output_text,
        "step": step,
        "status": "answered",
        "trace": state["trace"] + ["detailed_answer"],
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
        "classify",
        classify_node,
    )

    builder.add_node(
        "concise_answer",
        concise_answer_node,
    )

    builder.add_node(
        "detailed_answer",
        detailed_answer_node,
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
        "classify",
    )

    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "simple": "concise_answer",
            "complex": "detailed_answer",
        },
    )

    builder.add_edge(
        "concise_answer",
        "finish",
    )

    builder.add_edge(
        "detailed_answer",
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
        "route": "unclassified",
        "trace": [],
    }

    result = graph.invoke(initial_state)

    return result


def classify_node(
    state: AgentState,
) -> dict:
    step = state["step"] + 1

    question = state["question"].lower()

    complex_keywords = (
        "compare",
        "analyze",
        "architecture",
        "trade-off",
        "research",
        "investigate",
    )

    is_complex = any(keyword in question for keyword in complex_keywords)

    route = "complex" if is_complex else "simple"

    print(f"Step {step}: classify -> {route}")

    return {
        "step": step,
        "status": "classified",
        "route": route,
        "trace": state["trace"] + [f"classify:{route}"],
    }


def route_after_classify(
    state: AgentState,
) -> Literal[
    "simple",
    "complex",
]:
    if state["route"] == "complex":
        return "complex"

    return "simple"


def main() -> None:
    question = input("Question: ").strip()
    if not question:
        print("Question cannot be empty")
        return

    state = run_agent(question)

    print("\n=== Final State: ===")
    print(f"Status: {state['status']}")
    print(f"Steps: {state['step']}")
    print(f"Route: {state['route']}")

    print("Trace: " + " -> ".join(state["trace"]))

    print(f"Answer: {state['answer']}")


if __name__ == "__main__":
    main()

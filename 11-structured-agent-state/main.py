import os
from typing import Literal, TypedDict

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


def create_state(
    question: str,
) -> AgentState:
    return {
        "question": question,
        "answer": "",
        "step": 0,
        "status": "new",
        "trace": [],
    }


def prepare_state(
    state: AgentState,
) -> AgentState:
    state["step"] += 1
    state["status"] = "prepared"
    state["trace"].append("prepare ")

    return state


def answer_state(
    state: AgentState,
) -> AgentState:
    state["step"] += 1
    state["status"] = "answered"

    state["trace"].append("answer ")

    response = client.responses.create(
        model=MODEL,
        instructions=("You are a concise AI engineering learning assistant."),
        input=state["question"],
    )
    state["answer"] = response.output_text
    state["status"] = "answered"
    return state


def finish_node(
    state: AgentState,
) -> AgentState:
    state["step"] += 1
    state["status"] = "finished"

    state["trace"].append("finish ")

    return state


def run_agent(
    question: str,
) -> AgentState:
    state = create_state(question)
    state = prepare_state(state)
    state = answer_state(state)
    state = finish_node(state)

    print(f"Final State: {state}")
    return state


def main() -> None:
    question = input("Question: ").strip()

    if not question:
        print("Question cannot be empty.")
        return

    state = run_agent(question)

    print("\nFinal State:")

    print(f"Status: {state['status']}")
    print(f"Step: {state['step']}")
    print(f"Answer: {state['answer']}")

    print("\nTrace:" + " -> ".join(state["trace"]))


if __name__ == "__main__":
    main()

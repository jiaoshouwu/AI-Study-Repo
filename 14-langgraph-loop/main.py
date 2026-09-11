import os
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph
from openai import OpenAI

client = OpenAI()

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
)

MIN_WORDS = int(
    os.getenv(
        "MIN_WORDS",
        "50",
    )
)


MAX_ATTEMPTS = int(
    os.getenv(
        "MAX_ATTEMPTS",
        "2",
    )
)


class AgentState(TypedDict):
    question: str
    answer: str
    attempt: int
    quality_ok: bool

    decision: Literal[
        "undecided",
        "retry",
        "finish",
    ]

    status: Literal["new", "drafted", "evaluated", "revised", "finished"]

    trace: list[str]


def draft_node(
    state: AgentState,
) -> dict:
    attempt = state["attempt"] + 1

    print(f"Attempt {attempt}: draft")

    response = client.responses.create(
        model=MODEL,
        instructions=("Answer the user's question in only 1 or 2 short sentences"),
        input=state["question"],
    )

    return {
        "answer": response.output_text,
        "attempt": attempt,
        "status": "drafted",
        "trace": (state["trace"] + [f"draft:{attempt}"]),
    }


def evaluate_node(
    state: AgentState,
) -> dict:
    word_count = len(state["answer"].split())

    quality_ok = word_count >= MIN_WORDS

    if quality_ok:
        decision = "finish"
        result = "pass"

    elif state["attempt"] >= MAX_ATTEMPTS:
        decision = "finish"
        result = "max_attempts"

    else:
        decision = "retry"
        result = "retry"

    print(f"Evaluate: {word_count} words -> {result}")

    return {
        "quality_ok": quality_ok,
        "decision": decision,
        "status": "evaluated",
        "trace": (state["trace"] + [f"evaluate:{result}"]),
    }


def route_after_evaluate(
    state: AgentState,
) -> Literal[
    "retry",
    "finish",
]:
    if state["decision"] == "retry":
        return "retry"

    return "finish"


def revise_node(
    state: AgentState,
) -> dict:
    attempt = state["attempt"] + 1

    print(f"Attempt {attempt}: revise")

    prompt = (
        f"Question: \n"
        f"{state['question']}\n\n"
        f"Current answer: \n"
        f"{state['answer']} \n\n"
        "Rewrite the answer into a clear "
        "techinical explanation of about "
        "80 to 120 words"
    )

    response = client.responses.create(
        model=MODEL,
        instructions=("You are a concise AI engineering learning assistant."),
        input=prompt,
    )

    return {
        "answer": response.output_text,
        "attempt": attempt,
        "status": "revised",
        "trace": (state["trace"] + [f"revise:{attempt}"]),
    }


def finish_node(
    state: AgentState,
) -> dict:
    print("finish")

    return {
        "status": "finished",
        "trace": (state["trace"] + ["finish"]),
    }


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node(
        "draft",
        draft_node,
    )

    builder.add_node(
        "evaluate",
        evaluate_node,
    )

    builder.add_node(
        "revise",
        revise_node,
    )

    builder.add_node(
        "finish",
        finish_node,
    )

    builder.add_edge(
        START,
        "draft",
    )

    builder.add_edge(
        "draft",
        "evaluate",
    )
    builder.add_conditional_edges(
        "evaluate",
        route_after_evaluate,
        {"retry": "revise", "finish": "finish"},
    )

    builder.add_edge("revise", "evaluate")

    builder.add_edge(
        "finish",
        END,
    )

    return builder.compile()


def run_agent(
    question: str,
) -> AgentState:
    graph = build_graph()

    initial_state: AgentState = {
        "question": question,
        "answer": "",
        "attempt": 0,
        "quality_ok": False,
        "decision": "undecided",
        "status": "new",
        "trace": [],
    }

    result = graph.invoke(
        initial_state,
        {
            "recursion_limit": 10,
        },
    )

    return result


def validate_final_state(
    state: AgentState,
) -> None:
    assert state["status"] == "finished"

    assert state["attempt"] <= MAX_ATTEMPTS

    if state["quality_ok"]:
        assert "evaluate:pass" in state["trace"]


def main() -> None:
    question = input("Question: ").strip()

    if not question:
        print("Question can not be empty")

        return

    state = run_agent(question)

    validate_final_state(state)

    print("\n=== Final state ===")

    print(f"Status: {state['status']}")

    print(f"Attempts: {state['attempt']}")

    print(f"Quality OK: {state['quality_ok']}")

    print("Trace: " + " -> ".join(state["trace"]))

    print(f"\nAnswer:\n{state['answer']}")


if __name__ == "__main__":
    main()

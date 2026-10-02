import os
from typing import Literal, TypedDict, cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from openai import OpenAI

client = OpenAI()

MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.6",
)

WorkerName = Literal[
    "researcher",
    "coder",
]


class TeamState(TypedDict, total=False):
    request: str
    selected_agent: WorkerName
    answer: str
    trace: list[str]


def supervisor_node(
    state: TeamState,
) -> dict:
    response = client.responses.create(
        model=MODEL,
        instructions="""
You are the supervisor of a small AI team.

You have exactly two workers:

researcher
- factual research
- current information
- source-based comparison

coder
- write code
- debug code
- explain software implementation

Do NOT answer the user's task.

Return exactly ONE word:
researcher
or
coder
""",
        input=state["request"],
    )

    selected = response.output_text.strip().lower()

    allowed = {
        "researcher",
        "coder",
    }

    if selected not in allowed:
        raise RuntimeError(f"Invalid supervisor output: {selected}")

    worker = cast(
        WorkerName,
        selected,
    )

    print(
        "Supervisor selected:",
        worker,
    )

    return {
        "selected_agent": worker,
        "trace": (state.get("trace", []) + [f"supervisor:{worker}"]),
    }


def researcher_node(
    state: TeamState,
) -> dict:
    print("Running researcher...")

    response = client.responses.create(
        model=MODEL,
        instructions="""
You are the research specialist.

Answer the assigned request concisely.

Rules:
- Use web search when current facts matter.
- Prefer authoritative sources.
- Preserve useful citations.
- Separate facts from assumptions.
- Avoid writing application code unless
  a small snippet is needed.
""",
        tools=[
            {
                "type": "web_search",
            }
        ],
        input=state["request"],
    )

    return {
        "answer": response.output_text,
        "trace": (state["trace"] + ["researcher"]),
    }


def coder_node(
    state: TeamState,
) -> dict:
    print("Running coder...")

    response = client.responses.create(
        model=MODEL,
        instructions="""
You are the coding specialist.

Rules:
- Focus on software implementation.
- Write small executable examples.
- Explain important implementation choices.
- Help debug code.
- Do not perform web research.
""",
        input=state["request"],
    )

    return {
        "answer": response.output_text,
        "trace": (state["trace"] + ["coder"]),
    }


def route_worker(
    state: TeamState,
) -> WorkerName:
    return state["selected_agent"]


def build_graph() -> CompiledStateGraph:
    builder = StateGraph(TeamState)

    builder.add_node(
        "supervisor",
        supervisor_node,
    )

    builder.add_node(
        "researcher",
        researcher_node,
    )

    builder.add_node(
        "coder",
        coder_node,
    )

    builder.add_edge(
        START,
        "supervisor",
    )

    builder.add_conditional_edges(
        "supervisor",
        route_worker,
        {
            "researcher": "researcher",
            "coder": "coder",
        },
    )

    builder.add_edge(
        "researcher",
        END,
    )

    builder.add_edge(
        "coder",
        END,
    )

    return builder.compile()


def run_team(
    request: str,
) -> TeamState:
    graph = build_graph()

    initial_state: TeamState = {
        "request": request,
        "trace": [],
    }

    return graph.invoke(initial_state)


def main() -> None:
    request = input("Request: ").strip()

    if not request:
        print("Request cannot be empty.")
        return

    result = run_team(request)

    print("\n=== Team Result ===")

    print(
        "Selected agent:",
        result["selected_agent"],
    )

    print(
        "Trace:",
        " -> ".join(result["trace"]),
    )

    print("\nAnswer:\n" + result["answer"])


if __name__ == "__main__":
    main()

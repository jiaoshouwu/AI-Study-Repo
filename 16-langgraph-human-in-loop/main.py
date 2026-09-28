from typing import Literal, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, interrupt


class AgentState(TypedDict, total=False):
    request: str
    plan: str
    approved: bool
    review_reason: str

    status: Literal[
        "new",
        "planned",
        "executed",
        "cancelled",
    ]

    trace: list[str]


class ReviewDecision(TypedDict):
    approved: bool
    reason: str


def plan_node(
    state: AgentState,
) -> dict:
    plan = f"SIMULATED ACTION:{state['request']}"

    print("\nPlan:")
    print(plan)

    return {
        "plan": plan,
        "status": "planned",
        "trace": (state.get("trace", []) + ["plan"]),
    }


def review_node(
    state: AgentState,
) -> Command[Literal["execute", "cancel"]]:

    decision = interrupt(
        {
            "question": ("Do you approve this action?"),
            "plan": state["plan"],
        },
        response_schema=ReviewDecision,
    )

    approved = decision["approved"]
    reason = decision["reason"]

    if approved:
        return Command(
            update={
                "approved": True,
                "review_reason": reason,
                "trace": (state["trace"] + ["approved"]),
            },
            goto="execute",
        )

    return Command(
        update={
            "approved": False,
            "review_reason": reason,
            "trace": (state["trace"] + ["rejected"]),
        },
        goto="cancel",
    )


def execute_node(
    state: AgentState,
) -> dict:
    print("\nSIMUlATED EXECUTION:")
    print(state["plan"])

    return {
        "status": "executed",
        "trace": (state["trace"] + ["execute"]),
    }


def cancel_node(
    state: AgentState,
) -> dict:
    print("\nAction canncelled.")

    return {
        "status": "cancelled",
        "trace": (state["trace"] + ["cancel"]),
    }


def build_graph() -> CompiledStateGraph:
    builder = StateGraph(AgentState)

    builder.add_node(
        "plan",
        plan_node,
    )

    builder.add_node("review", review_node)

    builder.add_node("execute", execute_node)

    builder.add_node("cancel", cancel_node)

    builder.add_edge(
        START,
        "plan",
    )

    builder.add_edge(
        "plan",
        "review",
    )

    builder.add_edge(
        "execute",
        END,
    )

    builder.add_edge(
        "cancel",
        END,
    )

    return builder.compile(
        checkpointer=InMemorySaver(),
    )


def make_config(
    thread_id: str,
) -> dict:

    return {
        "configurable": {
            "thread_id": thread_id,
        }
    }


def main() -> None:
    graph = build_graph()

    config = make_config("approval-demo")

    request = input("Requested action:").strip()

    if not request:
        print("Request cannot be empty.")
        return

    initial_state: AgentState = {
        "request": request,
        "status": "new",
        "trace": [],
    }

    result = graph.invoke(
        initial_state,
        config,
    )

    interrupts = result.get(
        "__interrupt__",
        (),
    )

    if not interrupts:
        print("Expected interrupt was not received")
        return

    review = interrupts[0].value

    print("\n=== Human Review ===")
    print(review["question"])
    print(review["plan"])

    before = graph.get_state(config)

    print(
        "Before resume - next:",
        before.next,
    )

    answer = input("Approved? [y/n]:").strip().lower()

    reason = input("Reason:").strip()

    decision = {
        "approved": answer == "y",
        "reason": reason,
    }

    final_state = graph.invoke(
        Command(
            resume=decision,
        ),
        config,
    )

    after = graph.get_state(config)

    print("\n=== Final State ===")

    print(
        "Status:",
        final_state["status"],
    )

    print(
        "Approved:",
        final_state["approved"],
    )

    print(
        "Reason:",
        final_state["review_reason"],
    )

    print(
        "Trace:",
        " -> ".join(final_state["trace"]),
    )

    print(
        "After resume - next:",
        after.next,
    )


if __name__ == "__main__":
    main()

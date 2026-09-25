from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from .config import settings
from .llm import make_plan
from .models import AgentResponse, ChangePlan, IterationRecord
from .workspace import apply_changes, run_validation, snapshot_workspace


class AgentState(TypedDict, total=False):
    task: str
    iteration: int
    feedback: str
    plan: ChangePlan
    changed_files: list[str]
    validation_output: str
    validation_ok: bool
    history: list[IterationRecord]


def planner_node(state: AgentState) -> AgentState:
    snapshot = snapshot_workspace()
    plan = make_plan(
        task=state["task"],
        snapshot=snapshot,
        feedback=state.get("feedback", ""),
    )
    return {**state, "plan": plan}


def editor_node(state: AgentState) -> AgentState:
    plan = state["plan"]
    changed = apply_changes(plan.changes)
    return {**state, "changed_files": changed}


def validator_node(state: AgentState) -> AgentState:
    plan = state["plan"]
    ok, output = run_validation(plan.validation_commands)

    record = IterationRecord(
        iteration=state["iteration"],
        plan_summary=plan.summary,
        changed_files=state.get("changed_files", []),
        validation_output=output,
        success=ok,
    )
    history = [*state.get("history", []), record]

    return {
        **state,
        "validation_ok": ok,
        "validation_output": output,
        "feedback": output,
        "history": history,
    }


def route_after_validation(state: AgentState) -> str:
    if state["validation_ok"]:
        return "done"
    if state["iteration"] >= settings.max_iterations:
        return "done"
    return "retry"


def retry_node(state: AgentState) -> AgentState:
    return {
        **state,
        "iteration": state["iteration"] + 1,
    }


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("editor", editor_node)
    graph.add_node("validator", validator_node)
    graph.add_node("retry", retry_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "editor")
    graph.add_edge("editor", "validator")
    graph.add_conditional_edges(
        "validator",
        route_after_validation,
        {"retry": "retry", "done": END},
    )
    graph.add_edge("retry", "planner")
    return graph.compile()


AGENT_GRAPH = build_graph()


def run_agent(task: str) -> AgentResponse:
    final_state = AGENT_GRAPH.invoke(
        {
            "task": task,
            "iteration": 1,
            "feedback": "",
            "history": [],
        }
    )

    ok = bool(final_state.get("validation_ok"))
    history = final_state.get("history", [])
    summary = (
        "Task completed and validation passed."
        if ok
        else "The agent reached the retry limit before validation passed."
    )

    return AgentResponse(
        task=task,
        status="completed" if ok else "failed",
        summary=summary,
        iterations=history,
    )

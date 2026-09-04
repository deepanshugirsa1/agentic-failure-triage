"""
LangGraph-style triage state machine (skeleton).

This runs offline without LLM API keys. Future 60%: real LangGraph nodes,
tool orchestration, and evidence retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class TriageState:
    issues: list[dict]
    labels: list[int] = field(default_factory=list)
    keep: list[bool] = field(default_factory=list)
    routed: list[dict] = field(default_factory=list)
    proposals: list[dict] = field(default_factory=list)
    report: dict = field(default_factory=dict)


def node_cluster(state: TriageState, fn: Callable) -> TriageState:
    texts = [i["text"] for i in state.issues]
    labels, _meta = fn(texts)
    state.labels = list(map(int, labels))
    return state


def node_dedupe(state: TriageState, fn: Callable) -> TriageState:
    texts = [i["text"] for i in state.issues]
    # fn expects (texts, labels) and returns keep mask; pipeline supplies X
    state.keep = fn(state)
    return state


def node_route(state: TriageState, route_fn: Callable) -> TriageState:
    routed = []
    for i, issue in enumerate(state.issues):
        if state.keep and not state.keep[i]:
            continue
        r = route_fn(issue["text"], issue.get("category_hint"))
        routed.append({**issue, "owner": r, "cluster": state.labels[i] if state.labels else -1})
    state.routed = routed
    return state


def node_propose_fix(state: TriageState) -> TriageState:
    """Stub: propose fix template from category — LLM rewrite is future scope."""
    templates = {
        "perception": "Review detection thresholds near failure tile; add hard-negative mining.",
        "planning": "Inspect planner cost weights for stall corridor; replay scenario in sim.",
        "control": "Tune longitudinal controller; check comfort jerk limits on takeovers.",
        "localization": "Validate map tile freshness; re-run map matching confidence checks.",
    }
    props = []
    for issue in state.routed:
        cat = issue.get("category_hint", "default")
        props.append(
            {
                "issue_id": issue["issue_id"],
                "proposed_fix": templates.get(
                    cat, "Gather logs and metric deltas; escalate to Autonomy Eval."
                ),
                "evidence": {
                    "cluster": issue.get("cluster"),
                    "owner": issue.get("owner"),
                    "software_version": issue.get("software_version"),
                },
            }
        )
    state.proposals = props
    return state


def run_graph(state: TriageState, steps: list[Callable[[TriageState], TriageState]]) -> TriageState:
    for step in steps:
        state = step(state)
    state.report = {
        "input_issues": len(state.issues),
        "kept_after_dedupe": sum(state.keep) if state.keep else len(state.issues),
        "routed": len(state.routed),
        "proposals": len(state.proposals),
    }
    return state


# TODO (future 60%):
# - Replace stubs with langgraph.StateGraph
# - Tool nodes: fetch_metrics, similar_issues, open_ticket
# - Human review gate before routing to Slack/Jira

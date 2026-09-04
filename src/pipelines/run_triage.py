"""End-to-end offline triage pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.clustering.embed_cluster import cluster_issues, dedupe_within_clusters
from src.graph.triage_graph import (
    TriageState,
    node_propose_fix,
    node_route,
    run_graph,
)
from src.routing.owners import load_owners, route_issue


def load_jsonl(path: str) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/sample/failures.jsonl")
    parser.add_argument("--owners", default="configs/owners.yaml")
    parser.add_argument("--out", default="data/sample/triage_report.json")
    args = parser.parse_args()

    issues = load_jsonl(args.input)
    owners = load_owners(args.owners)
    texts = [i["text"] for i in issues]
    labels, (_vec, X, _model) = cluster_issues(texts)
    keep = dedupe_within_clusters(texts, labels, X)

    state = TriageState(issues=issues, labels=list(map(int, labels)), keep=keep)

    def route_node(s: TriageState) -> TriageState:
        return node_route(s, lambda text, cat: route_issue(text, cat, owners))

    state = run_graph(state, [route_node, node_propose_fix])
    # attach cluster/dedupe stats already on state
    out = {
        "summary": state.report,
        "proposals": state.proposals[:50],  # sample for report size
        "note": "Full LLM tool-orchestration and evidence packs are future scope (~60%).",
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(state.report, indent=2))
    print(f"Wrote report -> {args.out}")


if __name__ == "__main__":
    main()

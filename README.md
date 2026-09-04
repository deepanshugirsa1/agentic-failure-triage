# Agentic Failure-Triage Workflow for Autonomy Evaluation

LLM-powered workflow that triages detected driving failures: **cluster → deduplicate → attribute root cause → route to owners → propose fixes** with supporting evidence.

> **Status: ~40% complete** — clustering, owner routing, and LangGraph skeleton run offline on sample failures. Full LLM tool-calling, evidence retrieval, and production backlog integration are future scope.

## What works today (40%)

- Sample failure corpus generator (disengagements / soft stops / remote assist)
- Embeddings-based clustering scaffold (hash/TF-IDF style offline; swap-in for real embeddings)
- Deduplication of near-duplicate failure signatures
- Owner routing table (`configs/owners.yaml`)
- LangGraph-style state machine skeleton (`src/graph/triage_graph.py`)
- Candidate fix proposal stub from nearest historical cluster centroids

## Quick start

```bash
pip install -r requirements.txt
python -m src.data.sample_failures --n 500 --out data/sample/failures.jsonl
python -m src.pipelines.run_triage --input data/sample/failures.jsonl --out data/sample/triage_report.json
pytest tests/ -q
```

## Workflow (current)

```
failures → embed/cluster → dedupe → root-cause label (rule+stub) → owner route → fix proposal stub → report
```

## Future scope (remaining ~60%)

| Area | Planned work |
|------|----------------|
| LLM agents | Real LangGraph nodes with tool calls (metric lookup, log fetch, similar-issue search) |
| Embeddings | Sentence-transformer / OpenAI embeddings; HNSW index for 5k+ backlog |
| Root cause | Multi-signal attribution (map tile, weather, software version, metric deltas) |
| Evidence packs | Trace links, metric screenshots, proposed PR templates for eng review |
| Scale | Batch triage Airflow job; Slack/Jira routing; human-in-the-loop approval |

## Stack

Python, LangChain / LangGraph (scaffolded), scikit-learn, PyYAML, pytest

## License

MIT

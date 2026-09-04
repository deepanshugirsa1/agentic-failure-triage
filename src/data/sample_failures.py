"""Generate a synthetic autonomy failure backlog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


TEMPLATES = [
    ("perception", "False obstacle detection near {scene}; soft_stop triggered"),
    ("planning", "Planner stall at intersection {scene}; progress metric dropped"),
    ("control", "Hard brake / high jerk during lane change at {scene}"),
    ("localization", "Lane offset spike; map_match confidence low at {scene}"),
    ("planning", "Remote assist after trajectory oscillation on corridor {scene}"),
    ("perception", "Missed VRU detection proxy; manual_takeover at {scene}"),
]


def generate(n: int, seed: int = 42) -> list[dict]:
    rng = np.random.default_rng(seed)
    scenes = [f"tile_{i:04d}" for i in range(40)]
    rows = []
    for i in range(n):
        cat, tmpl = TEMPLATES[int(rng.integers(0, len(TEMPLATES)))]
        scene = scenes[int(rng.integers(0, len(scenes)))]
        # Intentionally duplicate some messages for dedupe demos
        if i % 17 == 0 and rows:
            text = rows[int(rng.integers(0, len(rows)))]["text"]
            cat = rows[-1]["category_hint"]
        else:
            text = tmpl.format(scene=scene)
        rows.append(
            {
                "issue_id": f"ISS-{i:05d}",
                "text": text,
                "category_hint": cat,
                "software_version": "v1.1.0" if i % 3 else "v1.0.0",
                "lat": 37.7 + float(rng.normal(0, 0.05)),
                "lon": -122.4 + float(rng.normal(0, 0.05)),
            }
        )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=500)
    parser.add_argument("--out", default="data/sample/failures.jsonl")
    args = parser.parse_args()
    rows = generate(args.n)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {len(rows)} failures -> {out}")


if __name__ == "__main__":
    main()

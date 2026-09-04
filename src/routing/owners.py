"""Route issues to owning teams from keyword / category hints."""

from __future__ import annotations

from pathlib import Path
import yaml


def load_owners(path: str = "configs/owners.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["owners"]


def route_issue(text: str, category_hint: str | None, owners: dict) -> dict:
    text_l = text.lower()
    if category_hint and category_hint in owners:
        o = owners[category_hint]
        return {"team": o["team"], "slack": o["slack"], "reason": f"category:{category_hint}"}
    for key, o in owners.items():
        if key == "default":
            continue
        for kw in o.get("keywords", []):
            if kw.lower() in text_l:
                return {"team": o["team"], "slack": o["slack"], "reason": f"keyword:{kw}"}
    d = owners["default"]
    return {"team": d["team"], "slack": d["slack"], "reason": "default"}

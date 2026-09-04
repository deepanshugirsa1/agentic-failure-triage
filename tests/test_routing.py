from src.routing.owners import route_issue


def test_route_perception():
    owners = {
        "perception": {"team": "Perception", "slack": "#p", "keywords": ["obstacle"]},
        "default": {"team": "Eval", "slack": "#e", "keywords": []},
    }
    r = route_issue("False obstacle detection", "perception", owners)
    assert r["team"] == "Perception"


def test_route_keyword():
    owners = {
        "control": {"team": "Control", "slack": "#c", "keywords": ["jerk"]},
        "default": {"team": "Eval", "slack": "#e", "keywords": []},
    }
    r = route_issue("High jerk event", None, owners)
    assert r["team"] == "Control"

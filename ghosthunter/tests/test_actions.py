"""Allowlist / action-registry tests. No Docker, no model calls."""
import actions
import pytest

TARGET = {
    "name": "Demo",
    "containers": ["api", "db"],
    "actions": {"start_container": {}, "restart_container": {}, "raise_memory_limit": {"max_mb": 512}, "escalate": {}},
}

def ok(decision):
    return actions.validate(decision, TARGET)[0]

def test_allows_known_action_on_allowlisted_container():
    assert ok({"action": "start_container", "params": {"name": "db"}})

def test_rejects_container_outside_allowlist():
    good, why = actions.validate({"action": "restart_container", "params": {"name": "prod-postgres"}}, TARGET)
    assert not good and "allowlist" in why

def test_rejects_unknown_action():
    good, why = actions.validate({"action": "rm_rf", "params": {}}, TARGET)
    assert not good and "not enabled" in why

def test_rejects_registered_but_disabled_action():
    t = {**TARGET, "actions": {"escalate": {}}}
    assert not actions.validate({"action": "start_container", "params": {"name": "db"}}, t)[0]

@pytest.mark.parametrize("mb,expected", [(256, True), (512, True), (513, False), (32, False), ("512", False)])
def test_memory_limit_guard_uses_target_limit(mb, expected):
    assert ok({"action": "raise_memory_limit", "params": {"name": "api", "mb": mb}}) is expected

def test_missing_param_rejected():
    assert not ok({"action": "raise_memory_limit", "params": {"name": "api"}})

def test_escalate_needs_no_container():
    assert ok({"action": "escalate", "params": {"reason": "unclear"}})

def test_prompt_lists_only_enabled_actions():
    block = actions.prompt_block({**TARGET, "actions": {"escalate": {}, "start_container": {}}})
    assert "start_container" in block and "escalate" in block and "raise_memory_limit" not in block

def test_custom_action_plugs_in():
    @actions.action("scale_up", {"name": str, "replicas": int}, "service is overloaded")
    def _scale(p, target, limits):
        return f"scaled {p['name']} to {p['replicas']}"
    t = {**TARGET, "actions": {**TARGET["actions"], "scale_up": {}}}
    d = {"action": "scale_up", "params": {"name": "api", "replicas": 3}}
    assert actions.validate(d, t)[0]
    assert actions.execute(d, t) == "scaled api to 3"
    assert "scale_up" in actions.prompt_block(t)
    del actions.REGISTRY["scale_up"]

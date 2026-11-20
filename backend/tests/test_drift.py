from app.services.drift import register, snapshot, compare
import json
def test_missing_critical():
    register("t-missing", json.dumps({"password": "x", "port": 80}), "json")
    s = snapshot("t-missing", json.dumps({"port": 80}), "json")
    c = compare("t-missing", s["id"])
    assert c["total_diffs"] == 1 and c["diffs"][0]["type"] == "missing" and c["diffs"][0]["severity"] == "critical"
def test_unexpected_low():
    register("t-extra", json.dumps({"port": 80}), "json")
    s = snapshot("t-extra", json.dumps({"port": 80, "extra": True}), "json")
    c = compare("t-extra", s["id"])
    assert c["diffs"][0]["type"] == "unexpected" and c["diffs"][0]["severity"] == "low"
def test_nested_changed():
    register("t-nested", json.dumps({"env": {"mode": "prod"}}), "json")
    s = snapshot("t-nested", json.dumps({"env": {"mode": "dev"}}), "json")
    c = compare("t-nested", s["id"])
    assert c["diffs"][0]["path"] == "env.mode" and c["diffs"][0]["type"] == "changed"
def test_array_changed():
    register("t-arr", json.dumps({"ports": [80, 443]}), "json")
    s = snapshot("t-arr", json.dumps({"ports": [80]}), "json")
    c = compare("t-arr", s["id"])
    assert c["diffs"][0]["path"] == "ports"
def test_yaml_compare():
    register("t-yaml", "port: 80\nmode: prod", "yaml")
    s = snapshot("t-yaml", "port: 8080\nmode: prod", "yaml")
    c = compare("t-yaml", s["id"])
    assert c["diffs"][0]["path"] == "port" and c["diffs"][0]["severity"] == "high"

import json
try:
    import yaml
except ImportError:
    yaml = None
from datetime import datetime, timezone
CONFIGS = {}
SNAPSHOTS = []
NEXT_SNAP = [1]
CRITICAL_KEYS = {"password", "secret", "replicas", "image"}
HIGH_KEYS = {"replicas", "port", "cpu", "memory", "image"}
def parse_config(text, fmt="json"):
    if fmt == "yaml":
        if yaml is None:
            return {"error": "PyYAML not installed"}
        try:
            return yaml.safe_load(text)
        except Exception as e:
            return {"error": f"YAML parse error: {e}"}
    try:
        return json.loads(text)
    except Exception as e:
        return {"error": f"JSON parse error: {e}"}
def register(name, expected_text, fmt="json"):
    parsed = parse_config(expected_text, fmt)
    if isinstance(parsed, dict) and "error" in parsed:
        return parsed
    CONFIGS[name] = {"name": name, "expected": parsed, "format": fmt, "created_at": datetime.now(timezone.utc).isoformat()}
    return CONFIGS[name]
def snapshot(name, observed_text, fmt=None):
    cfg = CONFIGS.get(name)
    if not cfg:
        return {"error": f"Config '{name}' not found"}
    parsed = parse_config(observed_text, fmt or cfg["format"])
    if isinstance(parsed, dict) and "error" in parsed:
        return parsed
    sid = NEXT_SNAP[0]; NEXT_SNAP[0] += 1
    s = {"id": sid, "config_name": name, "observed": parsed, "created_at": datetime.now(timezone.utc).isoformat()}
    SNAPSHOTS.append(s)
    return s
def diff(expected, observed, path=""):
    diffs = []
    if isinstance(expected, dict) and isinstance(observed, dict):
        for k in expected:
            p = f"{path}.{k}" if path else k
            if k not in observed:
                sev = "critical" if k in CRITICAL_KEYS else "high"
                diffs.append({"path": p, "type": "missing", "expected": expected[k], "observed": None, "severity": sev, "remediation": f"Restore missing property '{p}' to {expected[k]!r}"})
            else:
                diffs.extend(diff(expected[k], observed[k], p))
        for k in observed:
            if k not in expected:
                p = f"{path}.{k}" if path else k
                diffs.append({"path": p, "type": "unexpected", "expected": None, "observed": observed[k], "severity": "low", "remediation": f"Remove unexpected property '{p}' or add it to expected config"})
    elif isinstance(expected, list) and isinstance(observed, list):
        if expected != observed:
            diffs.append({"path": path or "root", "type": "changed", "expected": expected, "observed": observed, "severity": "medium", "remediation": f"Restore array at '{path or 'root'}' to expected value"})
    elif expected != observed:
        leaf = path.split(".")[-1] if path else ""
        if type(expected) != type(observed):
            sev = "critical"
        elif leaf in CRITICAL_KEYS:
            sev = "critical"
        elif leaf in HIGH_KEYS:
            sev = "high"
        else:
            sev = "medium"
        diffs.append({"path": path or "root", "type": "changed", "expected": expected, "observed": observed, "severity": sev, "remediation": f"Change '{path or 'root'}' back to {expected!r}"})
    return diffs
def compare(name, snapshot_id):
    cfg = CONFIGS.get(name)
    snap = next((s for s in SNAPSHOTS if s["id"] == snapshot_id), None)
    if not cfg:
        return {"error": "config not found"}
    if not snap:
        return {"error": "snapshot not found"}
    diffs = diff(cfg["expected"], snap["observed"])
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for d in diffs:
        counts[d["severity"]] += 1
    verdict = "IN SYNC - no drift" if not diffs else f"DRIFT DETECTED - {len(diffs)} difference(s)"
    return {"config_name": name, "snapshot_id": snapshot_id, "total_diffs": len(diffs), "counts": counts, "verdict": verdict, "diffs": diffs}
def dashboard():
    return {"configs": len(CONFIGS), "snapshots": len(SNAPSHOTS), "last_snapshot": SNAPSHOTS[-1]["id"] if SNAPSHOTS else None}
def seed():
    if CONFIGS:
        return len(CONFIGS)
    exp = {'replicas': 3, 'image': 'web:v1', 'port': 80, 'env': {'mode': 'prod', 'debug': False}}
    obs = {'replicas': 2, 'image': 'web:v1', 'port': 80, 'env': {'mode': 'prod', 'debug': True}, 'extra': True}
    register('web-app', json.dumps(exp), 'json')
    snapshot('web-app', json.dumps(obs), 'json')
    return len(CONFIGS)

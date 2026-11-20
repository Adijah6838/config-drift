import { useState, useEffect } from "react";
const API = "http://127.0.0.1:8014/api";
export default function App() {
  const [configs, setConfigs] = useState([]);
  const [snaps, setSnaps] = useState([]);
  const [result, setResult] = useState(null);
  const [name, setName] = useState("web-app");
  const [expected, setExpected] = useState(JSON.stringify({replicas: 3, image: "web:v1", port: 80}, null, 2));
  const [observed, setObserved] = useState(JSON.stringify({replicas: 2, image: "web:v1", port: 80, extra: true}, null, 2));
  const [fmt, setFmt] = useState("json");
  const [snapId, setSnapId] = useState(1);
  const load = async () => { const c = await (await fetch(`${API}/configs`)).json(); setConfigs(c.configs); const s = await (await fetch(`${API}/snapshots`)).json(); setSnaps(s.snapshots); };
  useEffect(() => { load(); }, []);
  const reg = async () => { const r = await fetch(`${API}/configs`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, expected_text: expected, format: fmt }) }); setResult(await r.json()); load(); };
  const snap = async () => { const r = await fetch(`${API}/snapshots`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, observed_text: observed, format: fmt }) }); setResult(await r.json()); load(); };
  const cmp = async () => { const r = await fetch(`${API}/compare?name=${name}&snapshot_id=${snapId}`); setResult(await r.json()); };
  const seed = async () => { await fetch(`${API}/seed`, { method: "POST" }); load(); };
  const sevColor = (s) => s === "critical" ? "#ffcccc" : s === "high" ? "#ffe6cc" : s === "medium" ? "#ffffcc" : "#e6ffe6";
  return (<div style={{ maxWidth: 900, margin: "auto", padding: 20, fontFamily: "sans-serif" }}>
    <h1>?? Config Drift Detection</h1><p>JSON / YAML comparison. Missing, unexpected, changed. Severity: critical / high / medium / low.</p>
    <input value={name} onChange={e => setName(e.target.value)} placeholder="Config name" style={{ padding: 10 }} /><select value={fmt} onChange={e => setFmt(e.target.value)} style={{ padding: 10, marginLeft: 8 }}><option value="json">json</option><option value="yaml">yaml</option></select><button onClick={seed} style={{ padding: 10, marginLeft: 8 }}>Seed</button>
    <div style={{ display: "flex", gap: 12, marginTop: 12 }}><div style={{ flex: 1 }}><b>Expected</b><textarea value={expected} onChange={e => setExpected(e.target.value)} style={{ width: "100%", height: 120, padding: 8 }} /><button onClick={reg} style={{ padding: 10, marginTop: 6 }}>Register Expected</button></div><div style={{ flex: 1 }}><b>Observed</b><textarea value={observed} onChange={e => setObserved(e.target.value)} style={{ width: "100%", height: 120, padding: 8 }} /><button onClick={snap} style={{ padding: 10, marginTop: 6 }}>Take Snapshot</button></div></div>
    <h3>Compare</h3><input type="number" value={snapId} onChange={e => setSnapId(Number(e.target.value))} style={{ padding: 10, width: 90 }} /><button onClick={cmp} style={{ padding: 10, marginLeft: 8 }}>Compare</button>
    {result && result.diffs && <div><h3>{result.verdict} - {result.total_diffs} diffs | Critical {result.counts.critical} | High {result.counts.high} | Medium {result.counts.medium} | Low {result.counts.low}</h3>{result.diffs.map((d, i) => <div key={i} style={{ background: sevColor(d.severity), padding: 10, marginTop: 6 }}><b>{d.path}</b> | {d.type} | {d.severity}<br />Expected: {JSON.stringify(d.expected)} ? Observed: {JSON.stringify(d.observed)}<br /><i>?? {d.remediation}</i></div>)}</div>}
    {result && !result.diffs && <pre style={{ background: "#eef", padding: 10 }}>{JSON.stringify(result, null, 2)}</pre>}
    <h3>Snapshots ({snaps.length})</h3>{snaps.map(s => <div key={s.id} style={{ padding: 6, borderBottom: "1px solid #eee" }}>#{s.id} {s.config_name} | {s.created_at} | {JSON.stringify(s.observed).slice(0, 100)}</div>)}
  </div>);
}

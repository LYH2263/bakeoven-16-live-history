import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

type Side = { batch_id: number; code: string; phase: string; start_min: number; end_min: number };
type Pair = { oven_id: number; oven_label: string; a: Side; b: Side };
type LogRow = { id: number; batch_code: string; oven_id: number; detail: string; created_at: string };

const phaseName = (p: string) => (p === "ferment" ? "发酵" : "烘烤");
function fmt(m: number) {
  const h = Math.floor(m / 60), mm = m % 60;
  return `${String(h).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

export default function ConflictsPage() {
  const [pairs, setPairs] = useState<Pair[]>([]);
  const [logs, setLogs] = useState<LogRow[]>([]);
  useEffect(() => {
    api<Pair[]>("/conflicts/current").then(setPairs);
    api<LogRow[]>("/conflicts").then(setLogs);
  }, []);
  return (<>
    <h2>冲突</h2>
    <div className="conflict-cols">
      <section>
        <h3>当前重叠 · 在排批次实时计算</h3>
        {pairs.length === 0 && (
          <div className="ok">在排批次无重叠（仅端点相接不算重叠）。</div>
        )}
        {pairs.map((p, i) => (
          <Link to="/gantt" className="overlap-pair" key={i} title="在甘特中查看对应色块">
            <div className="overlap-pair-oven">{p.oven_label}</div>
            {[p.a, p.b].map((s, k) => (
              <div className="overlap-side" key={k}>
                <span className="mono overlap-code">{s.code}</span>
                <span className={`phase-tag ${s.phase}`}>{phaseName(s.phase)}</span>
                <span className="mono">{fmt(s.start_min)}–{fmt(s.end_min)}</span>
              </div>
            ))}
          </Link>
        ))}
      </section>
      <section>
        <h3>历史拒绝记录 · 仅存档，不参与挡炉</h3>
        <table className="table"><thead><tr><th>时间</th><th>批次</th><th>炉位</th><th>详情</th></tr></thead>
        <tbody>{logs.map(c => <tr key={c.id}><td className="mono">{new Date(c.created_at).toLocaleString()}</td><td>{c.batch_code}</td><td>{c.oven_id}</td><td>{c.detail}</td></tr>)}</tbody></table>
      </section>
    </div>
  </>);
}

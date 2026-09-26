import { useEffect, useState } from "react";
import { api } from "../api/client";
type Pair = {
  oven_id: number; oven_label: string;
  batch_a_id: number; batch_a_code: string;
  batch_b_id: number; batch_b_code: string;
  phase_a: string; phase_b: string;
  a_start: number; a_end: number; b_start: number; b_end: number;
};
type C = { id: number; batch_code: string; oven_id: number; detail: string; created_at: string };
function fmt(m: number) { const h = Math.floor(m/60), mm = m%60; return `${String(h).padStart(2,"0")}:${String(mm).padStart(2,"0")}`; }
const phaseName = (p: string) => (p === "ferment" ? "发酵" : "烘烤");
export default function ConflictsPage() {
  const [pairs, setPairs] = useState<Pair[]>([]);
  const [rows, setRows] = useState<C[]>([]);
  useEffect(() => {
    api<Pair[]>("/conflicts/current").then(setPairs);
    api<C[]>("/conflicts").then(setRows);
  }, []);
  return (<>
    <h2>冲突</h2>
    <div className="conflict-cols">
      <section>
        <h3>当前重叠（按仍在排的批次实时计算）</h3>
        <table className="table"><thead><tr><th>批次 A</th><th>批次 B</th><th>炉位</th><th>阶段</th><th>A 起止</th><th>B 起止</th></tr></thead>
        <tbody>
          {pairs.map((p, i) => (
            <tr key={`${p.batch_a_id}-${p.batch_b_id}-${i}`}>
              <td className="mono">{p.batch_a_code}</td>
              <td className="mono">{p.batch_b_code}</td>
              <td>{p.oven_label}</td>
              <td>{phaseName(p.phase_a)}{p.phase_b !== p.phase_a ? `×${phaseName(p.phase_b)}` : ""}</td>
              <td className="mono">{fmt(p.a_start)}–{fmt(p.a_end)}</td>
              <td className="mono">{fmt(p.b_start)}–{fmt(p.b_end)}</td>
            </tr>
          ))}
          {!pairs.length && <tr><td colSpan={6}>当前无重叠（端点相接不算重叠）</td></tr>}
        </tbody></table>
      </section>
      <section>
        <h3>历史拒绝（仅存档，不占炉、不入甘特）</h3>
        <table className="table"><thead><tr><th>时间</th><th>批次</th><th>炉位</th><th>详情</th></tr></thead>
        <tbody>
          {rows.map(c => <tr key={c.id}><td className="mono">{new Date(c.created_at).toLocaleString()}</td><td>{c.batch_code}</td><td>{c.oven_id}</td><td>{c.detail}</td></tr>)}
          {!rows.length && <tr><td colSpan={4}>暂无拒绝记录</td></tr>}
        </tbody></table>
      </section>
    </div>
  </>);
}

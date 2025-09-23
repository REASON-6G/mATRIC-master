// frontend/src/routes/_layout/index.tsx
import { useEffect, useMemo, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { createFileRoute } from "@tanstack/react-router";
import { API_BASE, getToken } from "../../lib/auth"; // <— centralised auth

type AgentRow = { id: string; ap_id: string; configuration: Record<string, unknown>; onboard: boolean; };
type AgentPoint = { ts: string; value: number; key?: string | null; };
type AgentSeries = { agent_id: string; points: AgentPoint[] };

async function apiGet<T>(path: string): Promise<T> {
  const token = getToken();
  if (!token) throw new Error("No token found. Please sign in.");
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
    credentials: "include",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${path} failed: ${res.status} ${text}`);
  }
  return res.json();
}

async function getAgentDetails(): Promise<AgentRow[]> {
  return apiGet<AgentRow[]>("/metrics/agent_details");
}

async function getAgentData(agentApId: string, windowMinutes: number): Promise<AgentSeries> {
  const u = new URL(`${API_BASE}/metrics/agent_data`);
  u.searchParams.set("agent", agentApId);
  u.searchParams.set("window", String(windowMinutes));
  const token = getToken();
  if (!token) throw new Error("No token found. Please sign in.");
  const res = await fetch(u.toString(), {
    headers: { Authorization: `Bearer ${token}` },
    credentials: "include",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`agent_data failed: ${res.status} ${text}`);
  }
  return res.json();
}

function prepareChart(series: AgentSeries | null) {
  if (!series || series.points.length === 0) return { rows: [] as any[], keys: [] as string[] };
  const byKey: Record<string, AgentPoint[]> = {};
  for (const p of series.points) (byKey[p.key ?? "value"] ||= []).push(p);
  const allTs = Array.from(new Set(series.points.map(p => p.ts))).sort();
  const rows = allTs.map(ts => {
    const row: any = { ts, t: new Date(ts).getTime() };
    for (const [k, arr] of Object.entries(byKey)) {
      const f = arr.find(p => p.ts === ts);
      row[k] = typeof f?.value === "number" ? f.value : null;
    }
    return row;
  });
  return { rows, keys: Object.keys(byKey) };
}

function DashboardIndex(): JSX.Element {
  const [agents, setAgents] = useState<AgentRow[]>([]);
  const [agent, setAgent] = useState<string>("");
  const [windowMins, setWindowMins] = useState<number>(30);
  const [series, setSeries] = useState<AgentSeries | null>(null);
  const [loadingAgents, setLoadingAgents] = useState<boolean>(true);
  const [loadingSeries, setLoadingSeries] = useState<boolean>(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const rows = await getAgentDetails();
        if (!mounted) return;
        setAgents(rows);
        if (!agent && rows.length > 0) {
          const first = rows.find(r => r.onboard) ?? rows[0];
          setAgent(first.ap_id);
        }
      } catch (e: any) {
        setErr(e?.message ?? "Failed to load agents");
      } finally {
        setLoadingAgents(false);
      }
    })();
    return () => { mounted = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!agent) return;
    let mounted = true;
    setLoadingSeries(true);
    setErr(null);
    (async () => {
      try {
        const s = await getAgentData(agent, windowMins);
        if (!mounted) return;
        setSeries(s);
      } catch (e: any) {
        if (!mounted) return;
        setErr(e?.message ?? "Failed to load series");
        setSeries(null);
      } finally {
        if (mounted) setLoadingSeries(false);
      }
    })();
    return () => { mounted = false; };
  }, [agent, windowMins]);

  const prepared = useMemo(() => prepareChart(series), [series]);
  const tokenMissing = !getToken();

  return (
    <div style={{ display: "grid", gap: 16, padding: 16 }}>
      <h2 style={{ margin: 0 }}>Dashboard</h2>

      {tokenMissing && (
        <div style={{ color: "crimson" }}>
          You’re not signed in. Go to <b>User Settings</b> (or your login page) and sign in, or set the token via your existing flow.
        </div>
      )}

      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <div>
          <label style={{ display: "block", fontSize: 12, opacity: 0.8 }}>Agent (ap_id)</label>
          {loadingAgents ? (
            <div>Loading agents…</div>
          ) : (
            <select
              value={agent}
              onChange={(e) => setAgent(e.target.value)}
              style={{ padding: 8, borderRadius: 8, minWidth: 220 }}
            >
              {agents.map(a => (
                <option key={a.id} value={a.ap_id}>
                  {a.ap_id}{a.onboard ? "" : " (not onboarded)"}
                </option>
              ))}
            </select>
          )}
        </div>

        <div>
          <label style={{ display: "block", fontSize: 12, opacity: 0.8 }}>Window (minutes)</label>
          <input
            type="number"
            min={1}
            value={windowMins}
            onChange={(e) => setWindowMins(Math.max(1, Number(e.target.value) || 1))}
            style={{ padding: 8, borderRadius: 8, width: 120 }}
          />
        </div>
      </div>

      {err && <div style={{ color: "crimson" }}>{err}</div>}

      <div style={{ width: "100%", height: 380, border: "1px solid #eee", borderRadius: 12, padding: 8 }}>
        {loadingSeries ? (
          <div style={{ padding: 12 }}>Loading chart…</div>
        ) : prepared.rows.length === 0 ? (
          <div style={{ padding: 12 }}>No data in this window.</div>
        ) : (
          <ResponsiveContainer>
            <LineChart data={prepared.rows} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="t" type="number" domain={["auto", "auto"]} tickFormatter={(t: number) => new Date(t).toLocaleTimeString()} />
              <YAxis />
              <Tooltip labelFormatter={(t: number | string) => new Date(Number(t)).toLocaleString()} />
              <Legend />
              {prepared.keys.map((k) => (
                <Line key={k} type="monotone" dataKey={k} dot={false} strokeWidth={2} isAnimationActive={false} connectNulls />
              ))}
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

// keep this exact key for the index route under /_layout
export const Route = createFileRoute("/_layout/")({
  component: DashboardIndex,
});

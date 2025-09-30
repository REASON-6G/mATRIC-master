// src/lib/auth.ts
// Centralised API base + token storage + refresh helpers.

export const API_BASE = "http://localhost:8888/api/v1";

const LS_KEYS = ["jwt", "access_token", "token"] as const;

let refreshTimer: number | null = null;
let inFlightRefresh: Promise<string | null> | null = null;

export function getToken(): string {
  for (const k of LS_KEYS) {
    const v = typeof window !== "undefined" ? localStorage.getItem(k) : null;
    if (v) return v;
  }
  // last resort: non-HttpOnly cookie (not recommended)
  if (typeof document !== "undefined") {
    const m = document.cookie.match(/(?:^|;)\s*access_token=([^;]+)/);
    if (m) return decodeURIComponent(m[1]);
  }
  return "";
}

export function saveToken(token: string) {
  if (typeof window === "undefined" || !token) return;
  localStorage.setItem("jwt", token);
  // optional mirror cookie (non-HttpOnly) for any legacy code paths
  document.cookie = `access_token=${encodeURIComponent(token)}; path=/; SameSite=Lax`;
  scheduleProactiveRefresh(token);
}

export function clearToken() {
  if (typeof window === "undefined") return;
  for (const k of LS_KEYS) localStorage.removeItem(k);
  document.cookie = "access_token=; Max-Age=0; path=/; SameSite=Lax";
  if (refreshTimer) {
    window.clearTimeout(refreshTimer);
    refreshTimer = null;
  }
}

type ParsedJWT = { exp?: number; [k: string]: any };
function parseJwt(token: string): ParsedJWT | null {
  try {
    const [, payload] = token.split(".");
    if (!payload) return null;
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function msUntilExpiry(token: string): number | null {
  const parsed = parseJwt(token);
  if (!parsed?.exp) return null;
  const ms = parsed.exp * 1000 - Date.now();
  return ms;
}

function scheduleProactiveRefresh(token: string) {
  if (typeof window === "undefined") return;
  if (refreshTimer) {
    window.clearTimeout(refreshTimer);
    refreshTimer = null;
  }
  const ms = msUntilExpiry(token);
  if (ms == null) return; // cannot schedule without exp
  // refresh 60s before expiry (never schedule negative)
  const delay = Math.max(0, ms - 60_000);
  refreshTimer = window.setTimeout(() => {
    void refreshAccessToken(); // fire and forget; fetch wrapper will use it
  }, delay);
}

/** POST /token/refresh using HttpOnly refresh cookie; returns new access token or null. */
export async function refreshAccessToken(): Promise<string | null> {
  // Deduplicate concurrent refreshes
  if (inFlightRefresh) return inFlightRefresh;

  inFlightRefresh = (async () => {
    try {
      const res = await fetch(`${API_BASE}/token/refresh`, {
        method: "POST",
        credentials: "include", // send refresh cookie
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
      if (!res.ok) {
        // refresh failed (cookie missing/expired)
        clearToken();
        return null;
      }
      const data = await res.json().catch(() => null as any);
      const tok = data?.access_token;
      if (typeof tok === "string" && tok.length > 20) {
        saveToken(tok);
        return tok;
      }
      return null;
    } catch {
      clearToken();
      return null;
    } finally {
      inFlightRefresh = null;
    }
  })();

  return inFlightRefresh;
}

// Optional convenience for login pages
export async function login(username: string, password: string) {
  const res = await fetch(`${API_BASE}/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include", // so server can set refresh cookie
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`login failed: ${res.status} ${text}`);
  }
  const data = await res.json();
  if (!data?.access_token) throw new Error("login response missing access_token");
  saveToken(data.access_token);
  return data;
}

// Kick off proactive refresh for an already saved token on first load
const existing = getToken();
if (existing) scheduleProactiveRefresh(existing);

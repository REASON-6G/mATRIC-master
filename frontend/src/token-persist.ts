// src/token-persist.ts
// - Attach Bearer to API calls
// - Save any { access_token } found in responses
// - On 401 from API: try refresh once, then retry the request

import { API_BASE, getToken, saveToken, refreshAccessToken } from "./lib/auth";

const API_ORIGIN = (() => {
  try { return new URL(API_BASE).origin; } catch { return ""; }
})();

const origFetch = window.fetch.bind(window);

function needsAuth(url: string): boolean {
  return !!API_ORIGIN && url.startsWith(API_ORIGIN);
}

function normalise(input: RequestInfo | URL, init?: RequestInit): { url: string; init?: RequestInit; request?: Request } {
  if (typeof input === "string" || input instanceof URL) {
    return { url: String(input), init };
  }
  return { url: input.url, request: input as Request, init };
}

function addAuth(input: RequestInfo | URL, init?: RequestInit): [RequestInfo | URL, RequestInit | undefined] {
  try {
    const { url, request } = normalise(input, init);
    if (!needsAuth(url)) return [input, init];

    const token = getToken();
    if (!token) return [input, init];

    const existingHeaders =
      init?.headers ?? (request ? request.headers : undefined);

    const headers = new Headers(existingHeaders || undefined);
    if (!headers.has("Authorization")) headers.set("Authorization", `Bearer ${token}`);

    if (request) {
      const newReq = new Request(request, { headers });
      return [newReq, init];
    }
    const newInit: RequestInit = { ...(init || {}), headers };
    return [url, newInit];
  } catch {
    return [input, init];
  }
}

async function captureTokenFromResponse(res: Response) {
  try {
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) {
      const clone = res.clone();
      const data: any = await clone.json().catch(() => null);
      const tok = data?.access_token;
      if (typeof tok === "string" && tok.length > 20) {
        saveToken(tok);
      }
    }
    const hdr = res.headers.get("Authorization");
    if (hdr && hdr.toLowerCase().startsWith("bearer ")) {
      saveToken(hdr.slice(7));
    }
  } catch {
    // ignore
  }
}

async function retryOnceAfterRefresh(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const newTok = await refreshAccessToken();
  if (!newTok) return new Response(null, { status: 401 });
  const [i2, n2] = addAuth(input, init);
  return origFetch(i2, n2);
}

window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  const [i2, n2] = addAuth(input, init);
  let res = await origFetch(i2, n2);

  // If 401 from our API (not from login/refresh), try one refresh then retry
  try {
    const { url } = normalise(i2, n2);
    const isAuthEndpoint = url.includes("/token") || url.includes("/login");
    if (!isAuthEndpoint && needsAuth(url) && res.status === 401) {
      res = await retryOnceAfterRefresh(i2, n2);
    }
  } catch {
    // ignore
  }

  await captureTokenFromResponse(res);
  return res;
};

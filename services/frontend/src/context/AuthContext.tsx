'use client';

import { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from "react";
import { AxiosError, AxiosHeaders } from "axios";
import { jwtDecode } from "jwt-decode";
import api from "@/lib/api";

export interface User {
  id: string;
  username: string;
  email: string;
  role?: "admin" | "user";
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
}

interface MeResponse {
  id: string;
  username: string;
  email: string;
  full_name?: string | null;
  role: "admin" | "user";
  created_at?: string;
}

interface RefreshResponse {
  access_token: string;
}

interface JwtPayload {
  exp: number;
  [key: string]: unknown;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // ---- logout ----
  const logout = useCallback(() => {
    if (refreshTimeoutRef.current) clearTimeout(refreshTimeoutRef.current);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete api.defaults.headers.common["Authorization"];
    setUser(null);
  }, []);

  // ---- schedule proactive refresh ----
  const scheduleTokenRefresh = useCallback((token: string) => {
    try {
      const decoded = jwtDecode<JwtPayload>(token);
      const expiresInMs = decoded.exp * 1000 - Date.now();
      const refreshTime = Math.max(expiresInMs - 10_000, 0);

      if (refreshTimeoutRef.current) clearTimeout(refreshTimeoutRef.current);
      refreshTimeoutRef.current = setTimeout(() => {
        refreshAccessToken().catch(logout);
      }, refreshTime);
    } catch {
      // invalid token, do nothing
    }
  }, [logout]);

  // ---- refresh access token ----
  const refreshAccessToken = useCallback(async (): Promise<string> => {
    const refresh_token = localStorage.getItem("refresh_token");
    if (!refresh_token) throw new Error("No refresh token available");

    const res = await api.post<RefreshResponse>(
      "/api/auth/refresh",
      {},
      { headers: { Authorization: `Bearer ${refresh_token}` } }
    );

    const { access_token } = res.data;
    localStorage.setItem("access_token", access_token);
    api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    scheduleTokenRefresh(access_token);
    return access_token;
  }, [scheduleTokenRefresh]);

  // ---- axios interceptor for 401 ----
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      res => res,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          try {
            const newToken = await refreshAccessToken();
            if (error.config) {
              if (error.config.headers) {
                const headers =
                  error.config.headers instanceof AxiosHeaders
                    ? error.config.headers
                    : new AxiosHeaders(error.config.headers);

                headers.set("Authorization", `Bearer ${newToken}`);
                error.config.headers = headers;
              } else {
                error.config.headers = new AxiosHeaders({
                  Authorization: `Bearer ${newToken}`,
                });
              }

              return api.request(error.config);
            }
          } catch {
            logout();
          }
        }
        return Promise.reject(error);
      }
    );

    return () => api.interceptors.response.eject(interceptor);
  }, [refreshAccessToken, logout]);

  // ---- initial user fetch ----
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      scheduleTokenRefresh(token);
    }

    const fetchUser = async () => {
      try {
        const res = await api.get<MeResponse>("/api/auth/me");
        setUser({
          id: res.data.id,
          username: res.data.username,
          email: res.data.email,
          role: res.data.role,
        });
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [scheduleTokenRefresh]);

  // ---- login ----
  const login = useCallback(async (username: string, password: string) => {
    const res = await api.post<LoginResponse>("/api/auth/login", { username, password });
    const { access_token, refresh_token } = res.data;

    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
    scheduleTokenRefresh(access_token);

    const me = await api.get<MeResponse>("/api/auth/me");
    setUser({
      id: me.data.id,
      username: me.data.username,
      email: me.data.email,
      role: me.data.role,
    });
  }, [scheduleTokenRefresh]);

  // ---- register ----
  const register = useCallback(async (username: string, email: string, password: string) => {
    await api.post<MeResponse>("/api/auth/register", { username, email, password });
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};

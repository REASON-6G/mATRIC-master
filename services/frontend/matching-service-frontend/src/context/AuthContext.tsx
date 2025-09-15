'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import type { AxiosError } from "axios";
import * as jwt_decode from "jwt-decode";
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
  username: string;
  email: string;
  full_name?: string | null;
  role: string;
  created_at?: any;
  id: string;
}

interface RefreshResponse {
  access_token: string;
}

interface DecodedToken {
  exp: number; // expiry timestamp
  [key: string]: any;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshTimeout, setRefreshTimeout] = useState<NodeJS.Timeout | null>(null);

  // ---- helper: refresh access token ----
  const refreshAccessToken = async (): Promise<string> => {
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
  };

  // ---- schedule proactive refresh ----
  const scheduleTokenRefresh = (token: string) => {
    try {
      const decoded = jwt_decode<DecodedToken>(token);
      const expiresInMs = decoded.exp * 1000 - Date.now();
      const refreshTime = Math.max(expiresInMs - 10_000, 0); // refresh 10s before expiry

      if (refreshTimeout) clearTimeout(refreshTimeout);
      const timeout = setTimeout(() => {
        refreshAccessToken().catch(logout);
      }, refreshTime);
      setRefreshTimeout(timeout);
    } catch {
      // invalid token, do nothing
    }
  };

  // ---- axios response interceptor for 401 ----
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (res) => res,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          try {
            const newToken = await refreshAccessToken();
            if (error.config) {
              error.config.headers = {
                ...error.config.headers,
                Authorization: `Bearer ${newToken}`,
              };
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
  }, []);

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
          role: res.data.role as "admin" | "user",
        });
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  // ---- login ----
  const login = async (username: string, password: string) => {
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
      role: me.data.role as "admin" | "user",
    });
  };

  // ---- register ----
  const register = async (username: string, email: string, password: string) => {
    await api.post<MeResponse>("/api/auth/register", { username, email, password });
  };

  // ---- logout ----
  const logout = () => {
    if (refreshTimeout) clearTimeout(refreshTimeout);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    delete api.defaults.headers.common["Authorization"];
    setUser(null);
  };

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

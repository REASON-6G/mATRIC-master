import axios, { AxiosError, InternalAxiosRequestConfig, AxiosHeaders } from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

interface RefreshResponse {
  access_token: string;
}

const api = axios.create({
  baseURL: API_BASE,
  headers: new AxiosHeaders({ "Content-Type": "application/json" }),
});

// Request interceptor: always ensure headers exist
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (!config.headers) {
    config.headers = new AxiosHeaders();
  }

  const token = localStorage.getItem("access_token");
  if (token) {
    (config.headers as AxiosHeaders).set("Authorization", `Bearer ${token}`);
  }

  console.debug(`[API] Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`, config.data);

  return config;
});

// Response interceptor: handle 401
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      const refresh_token = localStorage.getItem("refresh_token");
      if (!refresh_token) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        return Promise.reject(error);
      }

      try {
        const res = await axios.post<RefreshResponse>(
          `${API_BASE}/api/auth/refresh`,
          {},
          { headers: new AxiosHeaders({ Authorization: `Bearer ${refresh_token}` }) }
        );
        const { access_token } = res.data;

        localStorage.setItem("access_token", access_token);

        // Update default headers safely
        api.defaults.headers.common = new AxiosHeaders({
          ...api.defaults.headers.common,
          Authorization: `Bearer ${access_token}`,
        });

        // Update failed request headers safely
        (originalRequest.headers as AxiosHeaders).set("Authorization", `Bearer ${access_token}`);

        return api(originalRequest);
      } catch {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

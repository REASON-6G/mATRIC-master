import axios, { AxiosError } from "axios";

const API_BASE = process.env.BACKEND_API_URL || "http://localhost:5000";

interface RefreshResponse {
  access_token: string;
}

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// Attach access token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }
  return config;
});

// Response interceptor: handle 401 by refreshing token
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      const refresh_token = localStorage.getItem("refresh_token");
      if (!refresh_token) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        return Promise.reject(error);
      }

      try {
        const res = await axios.post<RefreshResponse>(`${API_BASE}/api/auth/refresh`, { refresh_token });
        const { access_token } = res.data;

        // Save new token
        localStorage.setItem("access_token", access_token);
        // Update default headers for future requests
        api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
        // Update headers of the failed request and retry
        originalRequest.headers = {
          ...originalRequest.headers,
          Authorization: `Bearer ${access_token}`,
        };

        return api(originalRequest);
      } catch {
        // Failed to refresh token
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        return Promise.reject(error);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

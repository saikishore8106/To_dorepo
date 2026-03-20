/**
 * api.js — Centralized Axios API Client
 * 
 * Concepts covered:
 * - Axios instance with base URL (single source of truth)
 * - Request interceptor: auto-attaches JWT to every request header
 * - Response interceptor: handles 401 (auto-logout on token expiry)
 * - Organized API methods grouped by resource
 */

import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";

// Create a reusable axios instance
const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Request Interceptor ─────────────────────────────────────────
// Runs before EVERY request — attaches the JWT token automatically
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ── Response Interceptor ─────────────────────────────────────────
// Runs after EVERY response — handles global errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid → force logout
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ── Auth API ─────────────────────────────────────────────────────

export const authAPI = {
  register: (data) => api.post("/api/users/register", data),

  login: (username, password) => {
    // OAuth2 requires form data (not JSON) for the login endpoint
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);
    return api.post("/api/users/login", form, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
  },

  getMe: () => api.get("/api/users/me"),
};

// ── Tasks API ─────────────────────────────────────────────────────

export const tasksAPI = {
  list: (page = 1, pageSize = 10, status = null) => {
    const params = { page, page_size: pageSize };
    if (status) params.status_filter = status;
    return api.get("/api/tasks/", { params });
  },

  create: (data) => api.post("/api/tasks/", data),

  update: (id, data) => api.put(`/api/tasks/${id}`, data),

  delete: (id) => api.delete(`/api/tasks/${id}`),

  stats: () => api.get("/api/tasks/stats/summary"),
};

export default api;

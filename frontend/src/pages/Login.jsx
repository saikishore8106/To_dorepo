/**
 * Login.jsx — Login Page
 *
 * Concepts:
 * - Controlled form inputs with React useState
 * - Async API call with error handling
 * - JWT token storage in localStorage
 * - React Router navigation after login
 */

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";
import { authAPI } from "../api";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await authAPI.login(form.username, form.password);
      
      // Store JWT in localStorage
      localStorage.setItem("token", res.data.access_token);
      
      toast.success("Welcome back! 🎉");
      navigate("/dashboard");
    } catch (err) {
      const message = err.response?.data?.detail || "Login failed. Please try again.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-card">
        {/* Logo */}
        <div className="auth-logo">
          <div className="logo-icon">✅</div>
          <h1>Task Manager Pro</h1>
          <p>Sign in to manage your tasks</p>
        </div>

        {/* Error Alert */}
        {error && <div className="alert alert-error">{error}</div>}

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="login-username">Username</label>
            <input
              id="login-username"
              type="text"
              name="username"
              placeholder="your_username"
              value={form.username}
              onChange={handleChange}
              required
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="login-password">Password</label>
            <input
              id="login-password"
              type="password"
              name="password"
              placeholder="••••••••"
              value={form.password}
              onChange={handleChange}
              required
              autoComplete="current-password"
            />
          </div>

          <button
            id="login-submit"
            type="submit"
            className="btn btn-primary btn-full"
            disabled={loading}
          >
            {loading ? <span className="spinner" /> : "Sign In"}
          </button>
        </form>

        <hr className="divider" />

        <p style={{ textAlign: "center", fontSize: "0.88rem", color: "var(--text-muted)" }}>
          Don't have an account?{" "}
          <Link to="/register" style={{ color: "var(--primary-light)", fontWeight: 600 }}>
            Create one
          </Link>
        </p>

        {/* Demo credentials hint */}
        <div style={{
          marginTop: "1.25rem", padding: "0.75rem 1rem",
          background: "rgba(99,102,241,0.08)", borderRadius: "8px",
          border: "1px solid rgba(99,102,241,0.2)"
        }}>
          <p style={{ fontSize: "0.78rem", color: "var(--text-muted)", textAlign: "center" }}>
            🔐 <strong style={{ color: "var(--primary-light)" }}>Demo:</strong>{" "}
            Register a new account to get started
          </p>
        </div>
      </div>
    </div>
  );
}

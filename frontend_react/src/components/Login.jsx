// src/components/Login.jsx
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../api/api";

export default function Login({ setUser }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await login(username, password);
      const payload = res.data || {};
      const userData = {
        id: payload.user_id,
        username: payload.username,
        role: payload.role,
        full_name: payload.full_name || payload.username,
      };

      setUser(userData);
      localStorage.setItem("user", JSON.stringify(userData));

      if (userData.role === "admin") {
        navigate("/admin/dashboard");
      } else {
        navigate("/my-results");
      }
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Invalid username or password.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5 col-md-4">
      <h3 className="mb-3">🔐 Login</h3>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleLogin}>
        <input
          className="form-control mb-2"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          className="form-control mb-3"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button className="btn btn-primary w-100" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      <p className="mt-3 text-center">
        Don’t have an account?{" "}
        <Link to="/signup" className="text-decoration-none">
          Sign Up
        </Link>
      </p>
    </div>
  );
}

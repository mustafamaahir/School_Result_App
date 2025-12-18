// src/components/Signup.jsx
import React, { useState } from "react";
import { register } from "../api/api";
import { useNavigate } from "react-router-dom";

export default function Signup() {
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("student");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    setMessage("");
    setIsError(false);

    try {
      const payload = {
        full_name: fullName,
        username,
        password,
        role,
      };

      await register(payload);

      setMessage("✅ Account created successfully! You can now log in.");
      setIsError(false);

      setTimeout(() => navigate("/login"), 1200);
    } catch (error) {
      const backendMsg =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        "❌ Username already exists.";

      setMessage(backendMsg);
      setIsError(true);
    }
  };

  return (
    <div className="container mt-5 col-md-5">
      <h3 className="mb-3">📝 Create Account</h3>

      {message && (
        <div className={`alert ${isError ? "alert-danger" : "alert-success"}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSignup}>
        <input
          className="form-control mb-2"
          placeholder="Full Name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />

        <input
          className="form-control mb-2"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />

        <input
          className="form-control mb-2"
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <select
          className="form-select mb-3"
          value={role}
          onChange={(e) => setRole(e.target.value)}
        >
          <option value="student">Student</option>
          <option value="admin">Admin</option>
        </select>

        <button className="btn btn-success w-100">Sign Up</button>
      </form>
    </div>
  );
}
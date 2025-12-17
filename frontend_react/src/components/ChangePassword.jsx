// src/components/ChangePassword.jsx
import React, { useState } from "react";
import { changePassword } from "../api/api";

export default function ChangePassword({ user }) {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");

    if (newPassword !== confirmPassword) {
      setError("New password and confirm password do not match.");
      return;
    }

    setLoading(true);
    try {
      const res = await changePassword(user.id, oldPassword, newPassword);
      setMessage(res.data.message || "Password changed successfully.");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Failed to change password.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5 col-md-4">
      <h3 className="mb-3">🔑 Change Password</h3>

      {message && <div className="alert alert-success">{message}</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleChangePassword}>
        <input
          className="form-control mb-2"
          type="password"
          placeholder="Old Password"
          value={oldPassword}
          onChange={(e) => setOldPassword(e.target.value)}
          required
        />
        <input
          className="form-control mb-2"
          type="password"
          placeholder="New Password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
        />
        <input
          className="form-control mb-3"
          type="password"
          placeholder="Confirm New Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <button className="btn btn-primary w-100" disabled={loading}>
          {loading ? "Updating..." : "Change Password"}
        </button>
      </form>
    </div>
  );
}

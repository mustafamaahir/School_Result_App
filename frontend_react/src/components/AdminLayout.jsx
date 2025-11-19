// src/components/AdminLayout.jsx
import React from "react";
import { Link, Outlet, useLocation } from "react-router-dom";
import { FaChartBar, FaUpload, FaUsers, FaCog, FaSignOutAlt } from "react-icons/fa";

export default function AdminLayout() {
  const location = useLocation();
  const userRaw = localStorage.getItem("user");
  const user = userRaw ? JSON.parse(userRaw) : null;

  const linkStyle = (path) => ({
    textDecoration: "none",
    color: location.pathname === path ? "#0d6efd" : "#fff",
    display: "flex",
    gap: 8,
    alignItems: "center",
    fontWeight: location.pathname === path ? "700" : "500",
  });

  const handleLogout = () => {
    localStorage.removeItem("user");
    window.location.href = "/login";
  };

  return (
    <div className="d-flex" style={{ minHeight: "100vh" }}>
      <aside className="bg-dark text-white p-4" style={{ width: 260 }}>
        <div className="text-center mb-4">
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: "50%",
              margin: "0 auto",
              background: "linear-gradient(135deg,#667eea,#764ba2)",
              color: "#fff",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 28,
              fontWeight: 700,
            }}
          >
            {user?.username?.charAt(0)?.toUpperCase() || "A"}
          </div>
          <h5 className="mt-2 mb-0">Admin Panel</h5>
          <small className="text-muted">{user?.full_name || user?.username}</small>
        </div>

        <nav className="d-flex flex-column gap-2">
          <Link to="/admin/dashboard" style={linkStyle("/admin/dashboard")}>
            <FaChartBar /> Dashboard
          </Link>
          <Link to="/admin/upload-results" style={linkStyle("/admin/upload-results")}>
            <FaUpload /> Upload Results
          </Link>
          <Link to="/admin/students" style={linkStyle("/admin/students")}>
            <FaUsers /> Students
          </Link>
          <Link to="/admin/settings" style={linkStyle("/admin/settings")}>
            <FaCog /> Settings
          </Link>
        </nav>

        <div style={{ marginTop: "auto" }}>
          <button
            className="btn w-100 mt-4 d-flex align-items-center justify-content-center gap-2"
            style={{
              background: "linear-gradient(135deg,#f093fb,#f5576c)",
              color: "#fff",
              border: "none",
            }}
            onClick={handleLogout}
          >
            <FaSignOutAlt /> Logout
          </button>
        </div>
      </aside>

      <main className="flex-grow-1 bg-light p-4">
        <Outlet />
      </main>
    </div>
  );
}

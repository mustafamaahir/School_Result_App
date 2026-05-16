// src/components/AdminMenu.jsx
import React from "react";
import { useLocation, Link } from "react-router-dom";

export default function AdminMenu() {
  const location = useLocation();
  const linkStyle = (p) => ({
    textDecoration: "none",
    color: location.pathname === p ? "#007bff" : "#000",
  });

  return (
    <div
      style={{
        width: "240px",
        position: "fixed",
        top: 0,
        left: 0,
        height: "100vh",
        borderRight: "1px solid #ddd",
        padding: "20px",
      }}
    >
      <h5>Admin Menu</h5>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li><Link to="/admin/upload" style={linkStyle("/admin/upload")}>📤 Upload Results</Link></li>
        <li><Link to="/admin/students" style={linkStyle("/admin/students")}>👥 Students</Link></li>
        <li><Link to="/admin/dashboard" style={linkStyle("/admin/dashboard")}>📊 Dashboard</Link></li>
      </ul>
    </div>
  );
}
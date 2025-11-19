// src/components/AdminMenu.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";

export default function AdminMenu() {
  const location = useLocation();
  const linkStyle = (p) => ({ textDecoration: "none", color: location.pathname === p ? "#007bff" : "#000" });

//   return (
//     <div className="bg-light border rounded p-3 shadow-sm" style={{ width: 240, position: "fixed" }}>
//       <h5 className="text-center mb-4">⚙️ Admin Menu</h5>
//       <ul className="list-unstyled">
//         <li className="mb-3"><Link to="/admin/dashboard" style={linkStyle("/admin/dashboard")}>📊 Dashboard</Link></li>
//         <li className="mb-3"><Link to="/admin/upload-results" style={linkStyle("/admin/upload-results")}>📤 Upload Results</Link></li>
//         <li><Link to="/login" style={linkStyle("/logout")}>🚪 Logout</Link></li>
//       </ul>
//     </div>
//   );
}

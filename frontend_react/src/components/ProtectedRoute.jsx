// src/components/ProtectedRoute.jsx
import React from "react";
import { Navigate } from "react-router-dom";

/**
 * allowedRole: optional. If provided, the stored user.role must match.
 * children: component subtree to show when allowed.
 */
export default function ProtectedRoute({ allowedRole, children }) {
  const userRaw = localStorage.getItem("user");
  if (!userRaw) return <Navigate to="/login" replace />;

  try {
    const user = JSON.parse(userRaw);
    if (allowedRole && user.role !== allowedRole) {
      // not authorized for this role
      return <Navigate to="/login" replace />;
    }
    return children;
  } catch {
    return <Navigate to="/login" replace />;
  }
}

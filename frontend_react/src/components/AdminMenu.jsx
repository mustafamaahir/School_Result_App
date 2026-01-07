// src/components/AdminMenu.jsx
import React from "react";
import { Link, useLocation } from "react-router-dom";

export default function AdminMenu() {
  const location = useLocation();
  const linkStyle = (p) => ({ textDecoration: "none", color: location.pathname === p ? "#007bff" : "#000" });
  
}

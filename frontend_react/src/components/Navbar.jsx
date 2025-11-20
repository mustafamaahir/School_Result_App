// src/components/Navbar.jsx
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "./Navbar.css";

export default function Navbar({ user, setUser }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark custom-navbar shadow-sm px-3 py-2">
      <div className="container-fluid">

        <Link className="navbar-brand fw-bold" to="/">
          📘 DAARUL-FAOZ FOR ARABIC & ISLAMIC STUDIES
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarContent"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarContent">
          <ul className="navbar-nav ms-auto align-items-center">

            {!user && (
              <>
                <li className="nav-item me-3">
                  <Link to="/login" className="nav-link fw-semibold">
                    Login
                  </Link>
                </li>

                <li>
                  <Link to="/signup" className="btn btn-light btn-sm fw-semibold">
                    Sign Up
                  </Link>
                </li>
              </>
            )}

            {user && (
              <>
                {user.role === "student" && (
                  <li className="nav-item me-3">
                    <Link to="/my-results" className="nav-link fw-semibold">
                      My Results
                    </Link>
                  </li>
                )}

                {user.role === "admin" && (
                  <li className="nav-item me-3">
                    <Link to="/admin/dashboard" className="nav-link fw-semibold">
                      Admin Dashboard
                    </Link>
                  </li>
                )}

                <li className="nav-item me-3">
                  <span className="text-white fw-semibold">
                    👋 {user.full_name}
                  </span>
                </li>

                <li>
                  <button onClick={handleLogout} className="btn btn-light btn-sm fw-semibold">
                    Logout
                  </button>
                </li>
              </>
            )}

          </ul>
        </div>
      </div>
    </nav>
  );
}

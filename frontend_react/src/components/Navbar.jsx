// src/components/Navbar.jsx
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

export default function Navbar({ user, setUser }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm px-3 py-2">
      <div className="container-fluid">
        <Link className="navbar-brand fw-bold text-light" to="/">
          🎓 DAARUL-FAOZ FOR ARABIC AND ISLAMIC STUDIES
        </Link>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarContent"
          aria-controls="navbarContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navbarContent">
          <ul className="navbar-nav ms-auto align-items-center">
            {!user && (
              <>
                <li className="nav-item me-3">
                  <Link to="/login" className="nav-link text-white fw-semibold">
                    Login
                  </Link>
                </li>
                <li>
                  <Link to="/signup" className="btn btn-outline-light btn-sm">
                    Sign Up
                  </Link>
                </li>
              </>
            )}

            {user && (
              <>
                {user.role === "student" && (
                  <li className="nav-item me-3">
                    <Link to="/my-results" className="nav-link text-white">
                      My Results
                    </Link>
                  </li>
                )}

                <li className="nav-item me-3">
                  <span className="text-white fw-semibold">
                    👋 {user.full_name || user.username}{" "}
                    <small className="text-info">({user.role})</small>
                  </span>
                </li>

                <li className="nav-item">
                  <button
                    className="btn btn-outline-light btn-sm"
                    onClick={handleLogout}
                  >
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

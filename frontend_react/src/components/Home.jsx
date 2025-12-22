import React from "react";
import { Link } from "react-router-dom";
import "./Home.css";
import heroImage from "../assets/home-hero.png"; // adjust path relative to Home.jsx

export default function Home({ user }) {
  return (
    <div className="home-container">

      {/* HERO SECTION */}
      <div className="hero">
        <div className="hero-text">
          <h1>DAARUL-FAOZ FOR ARABIC & ISLAMIC STUDIES</h1>

          <p>
            Providing quality Arabic education, Qur’an studies, Islamic morals,
            discipline, and excellent character development for every student.
          </p>

          {!user ? (
            <div className="hero-buttons">
              <Link to="/login" className="btn-primary">Login</Link>
              <Link to="/signup" className="btn-secondary">Sign Up</Link>
            </div>
          ) : user.role === "admin" ? (
            <Link to="/admin/dashboard" className="btn-primary">
              Go to Admin Dashboard
            </Link>
          ) : (
            <Link to="/my-results" className="btn-primary">
              View My Results
            </Link>
          )}
        </div>

        <div className="hero-image">
          <img src={heroImage} alt="Students learning Arabic" />
        </div>
      </div>

      {/* WHY CHOOSE SECTION */}
      <h2 className="section-title">Why Students Choose Daarul-Faoz</h2>

      <div className="features">

        <div className="feature-card">
          <h3>Arabic & Islamic Education</h3>
          <p>
            Well-structured learning in Arabic language, Qur’an, and Islamic sciences.
          </p>
        </div>

        <div className="feature-card">
          <h3>Moral Training</h3>
          <p>
            We instill discipline, respect, honesty, and responsibility into students.
          </p>
        </div>

        <div className="feature-card">
          <h3>Character Building</h3>
          <p>
            We help shape confident, well-mannered, God-conscious individuals.
          </p>
        </div>

      </div>

      {/* FOOTER */}
      <footer className="footer">
        © 2025 DAARUL-FAOZ FOR ARABIC & ISLAMIC STUDIES. All rights reserved.
      </footer>
    </div>
  );
}

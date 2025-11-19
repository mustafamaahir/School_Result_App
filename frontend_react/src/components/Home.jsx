import React from "react";
import { Link } from "react-router-dom";

export default function Home({ user }) {
  return (
    <div className="container mt-5 text-center">
      {!user ? (
        <>
          <h2>🎓 Welcome to DAARUL-FAOZ FOR ARABIC AND ISLAMIC STUDIES</h2>
          <p className="lead mt-3">
            Manage student results efficiently. Please{" "}
            <Link to="/login">Login</Link> or{" "}
            <Link to="/signup">Sign Up</Link> to continue.
          </p>
        </>
      ) : user.role === "admin" ? (
        <>
          <h2 className="text-primary">👋 Welcome, {user.full_name}!</h2>
          <p className="lead mt-3">
            You can manage results, upload new data, and view class performance.
          </p>
          <Link to="/admin-dashboard" className="btn btn-primary mt-3">
            Go to Admin Dashboard
          </Link>
        </>
      ) : (
        <>
          <h2 className="text-success">👋 Welcome, {user.full_name}!</h2>
          <p className="lead mt-3">
            View your results and performance summaries below.
          </p>
          <Link to="/student-results" className="btn btn-success mt-3">
            View My Results
          </Link>
        </>
      )}
    </div>
  );
}

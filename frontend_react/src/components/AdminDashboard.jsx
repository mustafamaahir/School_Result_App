// src/components/AdminDashboard.jsx
import React, { useEffect, useState } from "react";
import { getAllResults } from "../api/api";
import Table from "react-bootstrap/Table";
import "bootstrap/dist/css/bootstrap.min.css";
import { FaChartBar, FaChalkboardTeacher, FaMedal, FaUserGraduate, FaArrowUp } from "react-icons/fa";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function AdminDashboard() {
  const [results, setResults] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [selectedClass, setSelectedClass] = useState("");
  const [selectedTerm, setSelectedTerm] = useState("");
  const [selectedSubject, setSelectedSubject] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getAllResults();
        const data = res.data || [];
        setResults(data);
        setFiltered(data);
      } catch (err) {
        console.error("Failed to load results:", err);
        setResults([]);
        setFiltered([]);
      }
    };
    fetchData();
  }, []);

  const classes = [...new Set(results.map((r) => r.student_class))].filter(Boolean);
  const terms = [...new Set(results.map((r) => r.term))].filter(Boolean);
  const subjects = [...new Set(results.map((r) => r.subject))].filter(Boolean);

  useEffect(() => {
    let temp = [...results];
    if (selectedClass) temp = temp.filter((r) => r.student_class === selectedClass);
    if (selectedTerm) temp = temp.filter((r) => r.term === selectedTerm);
    if (selectedSubject) temp = temp.filter((r) => r.subject === selectedSubject);
    setFiltered(temp);
  }, [selectedClass, selectedTerm, selectedSubject, results]);

  // summary numbers
  const averageScore =
    filtered.length > 0
      ? (filtered.reduce((acc, r) => acc + Number(r.percentage || 0), 0) / filtered.length).toFixed(1)
      : 0;

  const highestScore = filtered.length ? Math.max(...filtered.map((r) => Number(r.percentage || 0))) : 0;
  const lowestScore = filtered.length ? Math.min(...filtered.map((r) => Number(r.percentage || 0))) : 0;
  const topStudent = filtered.find((r) => Number(r.percentage || 0) === highestScore)?.name || "N/A";

  // class averages for chart
  const classesList = classes.length ? classes : ["No Class"];
  const avgPerClass = classesList.map((cls) => {
    const classData = results.filter((r) => r.student_class === cls);
    const avg = classData.length > 0 ? classData.reduce((acc, r) => acc + Number(r.percentage || 0), 0) / classData.length : 0;
    return { class: cls, average: Number(avg.toFixed(1)) };
  });

  return (
    <div className="container-fluid px-0">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2 className="fw-bold text-primary">
          <FaChartBar className="me-2" /> Admin Dashboard
        </h2>
      </div>

      {/* Filters */}
      <div className="row mb-4">
        <div className="col-md-3 mb-2">
          <label className="fw-semibold">Class</label>
          <select className="form-select" value={selectedClass} onChange={(e) => setSelectedClass(e.target.value)}>
            <option value="">All classes</option>
            {classes.map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>

        <div className="col-md-3 mb-2">
          <label className="fw-semibold">Term</label>
          <select className="form-select" value={selectedTerm} onChange={(e) => setSelectedTerm(e.target.value)}>
            <option value="">All terms</option>
            {terms.map((t) => <option key={t}>{t}</option>)}
          </select>
        </div>

        <div className="col-md-3 mb-2">
          <label className="fw-semibold">Subject</label>
          <select className="form-select" value={selectedSubject} onChange={(e) => setSelectedSubject(e.target.value)}>
            <option value="">All subjects</option>
            {subjects.map((s) => <option key={s}>{s}</option>)}
          </select>
        </div>
      </div>

      {/* Summary cards */}
      <div className="row text-center mb-4">
        <div className="col-md-4 mb-3">
          <div className="p-3 bg-primary text-white rounded shadow-sm">
            <FaChalkboardTeacher />
            <h6 className="mt-2">Average Score</h6>
            <h3 className="mb-0">{averageScore}%</h3>
          </div>
        </div>

        <div className="col-md-4 mb-3">
          <div className="p-3 bg-success text-white rounded shadow-sm">
            <FaUserGraduate />
            <h6 className="mt-2">Highest Scorer</h6>
            <h4 className="mb-0">{topStudent}</h4>
            <small>{highestScore}%</small>
          </div>
        </div>

        <div className="col-md-4 mb-3">
          <div className="p-3 bg-danger text-white rounded shadow-sm">
            <FaMedal />
            <h6 className="mt-2">Lowest Score</h6>
            <h3 className="mb-0">{lowestScore}%</h3>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="mb-5">
        <h5 className="fw-bold mb-3 d-flex align-items-center gap-2">
          <FaArrowUp /> Class Performance
        </h5>
        <div style={{ width: "100%", height: window.innerWidth < 768 ? 250 : 320 }}>
          <ResponsiveContainer>
            <BarChart data={avgPerClass}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="class" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="average" name="Average (%)" fill="#0d6efd" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Table */}
      <div>
        <h5 className="fw-bold mb-3">Results Summary</h5>
        <Table bordered hover responsive className="shadow-sm">
          <thead className="table-primary">
            <tr>
              <th>Session</th>
              <th>Term</th>
              <th>Class</th>
              <th>Subject</th>
              <th>Student</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length > 0 ? (
              filtered.map((r, i) => (
                <tr key={i}>
                  <td>{r.session}</td>
                  <td>{r.term}</td>
                  <td>{r.student_class}</td>
                  <td>{r.subject}</td>
                  <td>{r.name}</td>
                  <td>{r.percentage}%</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="text-center text-muted">No records found</td>
              </tr>
            )}
          </tbody>
        </Table>
      </div>
    </div>
  );
}

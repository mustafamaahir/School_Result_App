import { useEffect, useState } from "react";
import { getMyResults } from "../api/api";
import Table from "react-bootstrap/Table";
import Spinner from "react-bootstrap/Spinner";
import Alert from "react-bootstrap/Alert";
import Button from "react-bootstrap/Button";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Card from "react-bootstrap/Card";

export default function StudentResults({ user }) {
  const [results, setResults] = useState([]);
  const [selectedTerm, setSelectedTerm] = useState("All");
  const [selectedSession, setSelectedSession] = useState("All");
  const [academicAnalysis, setAcademicAnalysis] = useState("");
  const [studentName, setStudentName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [termPositions, setTermPositions] = useState({});
  const [sessions, setSessions] = useState([]);

  useEffect(() => {
    if (!user) return;

    const fetchResults = async () => {
      try {
        setLoading(true);
        setError(null);

        const res = await getMyResults(user.username);
        const data = res.data || {};

        const fetched = data.results || [];
        setResults(fetched);
        setAcademicAnalysis(data.academic_analysis || "");
        setStudentName(data.student_name || user.full_name || "");

        setTermPositions(data.term_positions || {});
        setSessions(["All", ...Array.from(new Set(fetched.map((r) => r.session)))]);

        // Auto-select latest term
        setSelectedTerm(data.latest_term || "All");
      } catch (err) {
        console.error(err);
        setError(err.response?.data?.detail || "Failed to fetch results");
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [user]);

  // Filter results by term/session
  const filteredResults = results.filter((r) => {
    return (selectedTerm === "All" || r.term === selectedTerm) &&
           (selectedSession === "All" || r.session === selectedSession);
  });

  const showStats = selectedTerm !== "All" && filteredResults.length > 0;
  
  const totalSubjects =
  termPositions?.[selectedTerm]?.total_subjects || filteredResults.length;

  const averageScore = showStats
    ? (filteredResults.reduce((acc, curr) => acc + Number(curr.percentage || 0), 0) / totalSubjects).toFixed(2)
    : 0;
  const highestScore = showStats ? Math.max(...filteredResults.map(r => r.percentage)) : 0;
  const lowestScore = showStats ? Math.min(...filteredResults.map(r => r.percentage)) : 0;
  const selectedTermPosition = termPositions[selectedTerm]?.position_label || "";

  const sortedTerms = ["All", "First Term", "Second Term", "Third Term"];

  return (
    <div className="container mt-4">
      <h3 className="mb-4 text-center text-primary">
        My Academic Results {studentName && ` - ${studentName}`}
      </h3>

      {loading ? (
        <div className="text-center my-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-2">Loading results...</p>
        </div>
      ) : error ? (
        <Alert variant="danger">{error}</Alert>
      ) : results.length === 0 ? (
        <Alert variant="info">No academic results available yet.</Alert>
      ) : (
        <>
          {/* Filters */}
          <Card className="mb-3 shadow-sm">
            <Card.Body>
              <div className="d-flex flex-wrap gap-3 align-items-center">
                <div>
                  <small className="text-muted d-block mb-1">Session:</small>
                  <ButtonGroup size="sm">
                    {sessions.map(session => (
                      <Button
                        key={session}
                        variant={selectedSession === session ? "primary" : "outline-primary"}
                        onClick={() => setSelectedSession(session)}
                      >
                        {session}
                      </Button>
                    ))}
                  </ButtonGroup>
                </div>
                <div>
                  <small className="text-muted d-block mb-1">Term:</small>
                  <ButtonGroup size="sm">
                    {sortedTerms.map(term => (
                      <Button
                        key={term}
                        variant={selectedTerm === term ? "primary" : "outline-primary"}
                        onClick={() => setSelectedTerm(term)}
                      >
                        {term}
                      </Button>
                    ))}
                  </ButtonGroup>
                </div>
              </div>
            </Card.Body>
          </Card>

          {/* Stats */}
          {showStats && (
            <Card className="mb-3 shadow-sm">
              <Card.Header className="bg-primary text-white">
                <h5 className="mb-0">Performance Summary ({selectedTerm})</h5>
              </Card.Header>
              <Card.Body>
                <div className="row text-center">
                  <div className="col-md-3 col-6 mb-2">
                    <p className="text-muted mb-1">Average Score</p>
                    <h4 className="text-primary">{averageScore}%</h4>
                  </div>
                  <div className="col-md-3 col-6 mb-2">
                    <p className="text-muted mb-1">Highest Score</p>
                    <h4 className="text-success">{highestScore}%</h4>
                  </div>
                  <div className="col-md-3 col-6 mb-2">
                    <p className="text-muted mb-1">Lowest Score</p>
                    <h4 className="text-danger">{lowestScore}%</h4>
                  </div>
                  <div className="col-md-3 col-6 mb-2">
                    <p className="text-muted mb-1">Subjects</p>
                    <h4>{termPositions[selectedTerm]?.subjects_taken || filteredResults.length} / {termPositions[selectedTerm]?.total_subjects || filteredResults.length}</h4>
                  </div>

                  {selectedTermPosition && (
                    <div className="col-12 mt-3">
                      <p className="text-muted mb-1">Position in Class</p>
                      <h3 className="text-info fw-bold">{selectedTermPosition}</h3>
                    </div>
                  )}
                </div>
              </Card.Body>
            </Card>
          )}

          {/* Detailed Table */}
          <Card className="shadow-sm mb-3">
            <Card.Header className="bg-dark text-white">
              <h5 className="mb-0">Detailed Results</h5>
            </Card.Header>
            <Card.Body className="p-0">
              <Table bordered hover responsive className="mb-0">
                <thead className="table-light text-center">
                  <tr>
                    <th>Session</th>
                    <th>Term</th>
                    <th>Class</th>
                    <th>Subject</th>
                    <th>Score (%)</th>
                    <th>Class Min</th>
                    <th>Class Max</th>
                    <th>Class Median</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredResults.length > 0 ? (
                    filteredResults.map((r, i) => (
                      <tr key={i}>
                        <td>{r.session}</td>
                        <td>{r.term}</td>
                        <td>{r.student_class}</td>
                        <td className="fw-bold">{r.subject}</td>
                        <td className="text-center">
                          <span className={`badge ${
                            r.percentage >= 70 ? "bg-success" :
                            r.percentage >= 50 ? "bg-warning text-dark" :
                            "bg-danger"
                          }`}>{r.percentage}%</span>
                        </td>
                        <td className="text-center">{r.min_score_in_class}</td>
                        <td className="text-center">{r.max_score_in_class}</td>
                        <td className="text-center">{r.median_score_in_class}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="8" className="text-center text-muted py-4">
                        No results match the selected filters.
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          {/* Academic Analysis */}
          {academicAnalysis && (
            <Card className="mb-4 shadow">
              <Card.Header
                className="bg-gradient"
                style={{ background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}
              >
                <h5 className="mb-0 text-white">
                  <i className="bi bi-clipboard-data me-2"></i>
                  Academic Performance Analysis
                </h5>
              </Card.Header>
              <Card.Body className="bg-light">
                <div className="p-4 bg-white rounded border-start border-primary border-4">
                  <p className="mb-0" style={{ whiteSpace: "pre-wrap", lineHeight: "1.8", fontSize: "1.05rem", color: "#2c3e50" }}>
                    {academicAnalysis}
                  </p>
                </div>
              </Card.Body>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

import { useState } from "react";
import { uploadResults } from "../api/api";
import AdminMenu from "./AdminMenu.jsx";

export default function UploadResults() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return setMessage("Please select a file to upload.");
    try {
      const res = await uploadResults(file);
      const msg = res.data;
      setMessage(`✅ ${msg.message || "Upload successful!"}`);
    } catch {
      setMessage("❌ Upload failed. Check server connection.");
    }
  };

  return (
    <div className="d-flex">
      <AdminMenu />
      <div className="container mt-5 col-md-6" style={{ marginLeft: "260px" }}>
        <h3>📤 Upload Results</h3>
        {message && <div className="alert alert-info">{message}</div>}
        <form onSubmit={handleUpload}>
          <input
            type="file"
            className="form-control mb-3"
            accept=".xlsx,.csv"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <button className="btn btn-success w-100">Upload</button>
        </form>
      </div>
    </div>
  );
}
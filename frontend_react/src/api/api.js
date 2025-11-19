import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// ---------- AUTH ----------
export const login = (username, password) =>
  api.post("/auth/login", { username, password });

export const register = (data) =>
  api.post("/auth/register", data);

// ---------- RESULTS ----------
export const getAllResults = () => api.get("/results/all");

export const uploadResults = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/results/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

// MUST include class_name because backend ranking uses (term + class)
export const getMyResults = (username, term, student_class) =>
  api.get(`/results/myResults`, { params: { username, term, student_class } });

// Optional student report (still must include term + class if you use it)
export const getStudentReport = (username, term) =>
  api.get(`/results/myResults`, { params: { username, term } });

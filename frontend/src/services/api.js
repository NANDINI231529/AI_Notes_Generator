import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const authApi = {
  login: (payload) => api.post("/auth/login", payload),
  signup: (payload) => api.post("/auth/signup", payload),
  me: () => api.get("/auth/me"),
};

export const documentApi = {
  upload: (files) => {
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    return api.post("/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export const notesApi = {
  generate: (documentId) => api.post("/notes/generate", { document_id: documentId }),
  save: (payload) => api.post("/notes/", payload),
  list: () => api.get("/notes/"),
  remove: (noteId) => api.delete(`/notes/${noteId}`),
};

export function getApiError(err, fallback = "Something went wrong") {
  const detail = err.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg).join(", ");
  if (err.code === "ERR_NETWORK") return "Backend is not running on http://localhost:8000";
  return fallback;
}

export default api;

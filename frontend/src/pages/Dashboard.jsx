import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";
import Sidebar from "../components/Sidebar.jsx";
import UploadBox from "../components/UploadBox.jsx";
import { documentApi, notesApi } from "../services/api.js";

export default function Dashboard() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const uploadAndGenerate = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const documentResponse = await documentApi.upload(file);
      const notesResponse = await notesApi.generate(documentResponse.data.id);
      sessionStorage.setItem("generatedNotes", JSON.stringify(notesResponse.data));
      navigate("/generated");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not process this document");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-body">
        <Sidebar />
        <main className="workspace">
          <section className="page-heading">
            <p>Login → Upload Document → Extract Text → Generate Notes → Save</p>
            <h1>Generate AI notes from any study file</h1>
          </section>
          <UploadBox file={file} onFileChange={setFile} onUpload={uploadAndGenerate} loading={loading} />
          {error && <p className="error center">{error}</p>}
        </main>
      </div>
    </div>
  );
}

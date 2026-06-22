import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar.jsx";
import Sidebar from "../components/Sidebar.jsx";
import { notesApi } from "../services/api.js";
import { cleanNoteText } from "../utils/notes.js";

export default function GeneratedNotes() {
  const navigate = useNavigate();
  const generated = useMemo(() => JSON.parse(sessionStorage.getItem("generatedNotes") || "null"), []);
  const [mode, setMode] = useState("short");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const displayedNotes = generated
    ? cleanNoteText(mode === "short" ? generated.short_notes : generated.detailed_notes)
    : "";

  const save = async () => {
    if (!generated) return;
    setSaving(true);
    setMessage("");
    try {
      await notesApi.save({
        document_id: generated.document_id,
        title: generated.title,
        short_notes: cleanNoteText(generated.short_notes),
        detailed_notes: cleanNoteText(generated.detailed_notes),
      });
      setMessage("Notes saved to your profile.");
    } catch (err) {
      setMessage(err.response?.data?.detail || "Could not save notes");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-body">
        <Sidebar />
        <main className="workspace">
          <section className="notes-view">
            <div className="notes-header">
              <div>
                <p>Generated notes</p>
                <h1>{generated?.title || "No generated notes yet"}</h1>
              </div>
              {generated && (
                <div className="actions">
                  <div className="segmented">
                    <button className={mode === "short" ? "active" : ""} onClick={() => setMode("short")}>Short</button>
                    <button className={mode === "detailed" ? "active" : ""} onClick={() => setMode("detailed")}>Detailed</button>
                  </div>
                  <button className="primary" onClick={save} disabled={saving}>{saving ? "Saving..." : "Save Notes"}</button>
                </div>
              )}
            </div>
            {generated ? (
              <pre className="notes-output">{displayedNotes}</pre>
            ) : (
              <button className="primary" onClick={() => navigate("/dashboard")}>Upload a document</button>
            )}
            {message && <p className="success">{message}</p>}
          </section>
        </main>
      </div>
    </div>
  );
}

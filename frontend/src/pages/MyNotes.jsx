import { useEffect, useState } from "react";
import Navbar from "../components/Navbar.jsx";
import NoteCard from "../components/NoteCard.jsx";
import ProfileDropdown from "../components/ProfileDropdown.jsx";
import Sidebar from "../components/Sidebar.jsx";
import { notesApi } from "../services/api.js";

export default function MyNotes() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadNotes = async () => {
    setLoading(true);
    const { data } = await notesApi.list();
    setNotes(data);
    setLoading(false);
  };

  useEffect(() => {
    loadNotes().catch(() => setLoading(false));
  }, []);

  const remove = async (id) => {
    await notesApi.remove(id);
    setNotes((current) => current.filter((note) => note.id !== id));
  };

  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-body">
        <Sidebar />
        <main className="workspace">
          <ProfileDropdown />
          <section className="page-heading compact">
            <p>Saved notes</p>
            <h1>Your profile library</h1>
          </section>
          {loading ? (
            <p className="muted">Loading notes...</p>
          ) : notes.length ? (
            <div className="notes-grid">
              {notes.map((note) => <NoteCard key={note.id} note={note} onDelete={remove} />)}
            </div>
          ) : (
            <p className="empty-state">Saved generated notes will appear here.</p>
          )}
        </main>
      </div>
    </div>
  );
}

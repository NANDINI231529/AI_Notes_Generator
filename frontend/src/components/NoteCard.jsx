import { Calendar, Trash2 } from "lucide-react";

export default function NoteCard({ note, onDelete }) {
  const date = new Date(note.created_at).toLocaleDateString();

  return (
    <article className="note-card">
      <div>
        <h3>{note.title}</h3>
        <p className="note-date">
          <Calendar size={15} />
          {date}
        </p>
      </div>
      <p>{note.short_notes}</p>
      {onDelete && (
        <button className="ghost danger" onClick={() => onDelete(note.id)}>
          <Trash2 size={17} />
          Delete
        </button>
      )}
    </article>
  );
}

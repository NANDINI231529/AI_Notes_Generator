from sqlalchemy.orm import Session

from models.note import Note
from schemas import SaveNoteIn


def create_note(db: Session, user_id: int, payload: SaveNoteIn) -> Note:
    note = Note(
        title=payload.title.strip() or "Untitled Notes",
        short_notes=payload.short_notes,
        detailed_notes=payload.detailed_notes,
        document_id=payload.document_id,
        user_id=user_id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

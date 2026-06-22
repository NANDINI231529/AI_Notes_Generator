from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from database.session import get_db
from models.document import Document
from models.note import Note
from models.user import User
from schemas import GenerateNotesIn, NoteOut, SaveNoteIn
from services.auth_service import get_current_user
from services.gemini_service import generate_notes
from services.note_service import create_note

router = APIRouter()


@router.post("/generate")
def generate(payload: GenerateNotesIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    document = db.scalar(
        select(Document).where(Document.id == payload.document_id, Document.user_id == current_user.id)
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    notes = generate_notes(document.extracted_text)
    return {"title": document.filename, "document_id": document.id, **notes}


@router.post("/", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def save(payload: SaveNoteIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.document_id:
        document = db.scalar(
            select(Document).where(Document.id == payload.document_id, Document.user_id == current_user.id)
        )
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
    return create_note(db, current_user.id, payload)


@router.get("/", response_model=list[NoteOut])
def list_notes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.scalars(
        select(Note).where(Note.user_id == current_user.id).order_by(desc(Note.created_at))
    ).all()


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.scalar(select(Note).where(Note.id == note_id, Note.user_id == current_user.id))
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return None

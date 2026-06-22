from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database.session import get_db
from models.document import Document
from models.user import User
from schemas import DocumentOut
from services.auth_service import get_current_user
from services.pdf_service import ALLOWED_EXTENSIONS, extract_text_from_upload

router = APIRouter()
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Upload PDF, DOCX, TXT, JPG, or PNG files only")

    content = await file.read()
    try:
        extracted_text = extract_text_from_upload(file.filename or "upload", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Could not extract text from this file") from exc

    if not extracted_text.strip():
        raise HTTPException(status_code=422, detail="No readable text found in this file")

    stored_name = f"{uuid4().hex}{ext}"
    (UPLOAD_DIR / stored_name).write_bytes(content)

    document = Document(
        filename=file.filename or stored_name,
        content_type=file.content_type or "application/octet-stream",
        extracted_text=extracted_text,
        user_id=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

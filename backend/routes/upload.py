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
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not files:
        raise HTTPException(status_code=400, detail="Select at least one file")

    extracted_sections: list[str] = []
    stored_filenames: list[str] = []
    content_types: set[str] = set()

    for file in files:
        original_name = file.filename or "upload"
        ext = Path(original_name).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"{original_name}: upload PDF, DOCX, TXT, JPG, or PNG files only",
            )

        content = await file.read()
        try:
            extracted_text = extract_text_from_upload(original_name, content)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=f"{original_name}: {exc}") from exc
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"{original_name}: could not extract text") from exc

        if not extracted_text.strip():
            raise HTTPException(status_code=422, detail=f"{original_name}: no readable text found")

        stored_name = f"{uuid4().hex}{ext}"
        (UPLOAD_DIR / stored_name).write_bytes(content)
        stored_filenames.append(original_name)
        content_types.add(file.content_type or "application/octet-stream")
        extracted_sections.append(f"Source file: {original_name}\n\n{extracted_text.strip()}")

    combined_text = "\n\n---\n\n".join(extracted_sections)
    display_name = stored_filenames[0]
    if len(stored_filenames) > 1:
        display_name = f"{len(stored_filenames)} files: {', '.join(stored_filenames[:3])}"
    if len(stored_filenames) > 3:
        display_name += f", +{len(stored_filenames) - 3} more"

    document = Document(
        filename=display_name,
        content_type="mixed" if len(content_types) > 1 else next(iter(content_types)),
        extracted_text=combined_text,
        user_id=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

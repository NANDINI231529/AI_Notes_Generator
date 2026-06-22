from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class GenerateNotesIn(BaseModel):
    document_id: int


class SaveNoteIn(BaseModel):
    document_id: int | None = None
    title: str
    short_notes: str
    detailed_notes: str


class DocumentOut(BaseModel):
    id: int
    filename: str
    content_type: str
    extracted_text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NoteOut(BaseModel):
    id: int
    title: str
    short_notes: str
    detailed_notes: str
    document_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}

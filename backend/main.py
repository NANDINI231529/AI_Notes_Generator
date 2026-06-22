from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import Base, engine
from models import document, note, user
from routes import auth, notes, upload

app = FastAPI(title="AI Notes Generator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(notes.router, prefix="/api/notes", tags=["Notes"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}

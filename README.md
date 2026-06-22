# AI Notes Generator

Full-stack AI Notes Generator built with React, FastAPI, PostgreSQL, JWT authentication, and Gemini.

## Features

- Login and signup with JWT auth
- Upload PDF, DOCX, TXT, JPG, and PNG
- Extract document text
- Generate AI short and detailed notes
- Toggle generated notes view
- Save notes to PostgreSQL
- View and delete saved notes in the user profile

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

By default, the backend uses a local SQLite database file so it can run immediately.

For PostgreSQL, create a database named `ai_notes_generator`, then set environment variables as needed:

```bash
set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_notes_generator
set JWT_SECRET_KEY=replace-with-a-secure-secret
set GEMINI_API_KEY=your-gemini-api-key
```

For image OCR, install Tesseract OCR on your system so `pytesseract` can use it.

Run the API:

```bash
uvicorn main:app --reload
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and expects the backend at `http://localhost:8000/api`.

## Workflow

Login -> Upload Document -> Extract Text -> Generate Notes -> Short/Detailed Toggle -> Save Notes -> View Notes in Profile.

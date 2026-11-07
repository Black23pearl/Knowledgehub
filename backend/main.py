from fastapi import FastAPI
from sqlalchemy import text

from db import engine
from schemas import NoteCreate, NoteOut

app = FastAPI()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/hello/{name}")
def hello(name: str):
    return {"message": f"Hello, {name}!"}


@app.get("/api/notes", response_model=list[NoteOut])
def list_notes():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, title, content, created_at FROM notes ORDER BY created_at DESC")
        )
        return [dict(row) for row in result.mappings()]


@app.post("/api/notes", response_model=NoteOut, status_code=201)
def create_note(note: NoteCreate):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "INSERT INTO notes (title, content) VALUES (:title, :content) "
                "RETURNING id, title, content, created_at"
            ),
            {"title": note.title, "content": note.content},
        )
        row = result.mappings().one()
        conn.commit()
    return dict(row)
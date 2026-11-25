from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

# Note model with validation
class Note(BaseModel):
    id: int = Field(gt=0)
    title: str = Field(min_length=3, max_length=100)
    content: str = Field(min_length=5, max_length=1000)


# Temporary in-memory storage
notes_storage = []


# Reusable 404 exception
def note_not_found():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Note not found. Please provide a valid note ID."
    )


# POST: Create a new note
@app.post("/notes", status_code=status.HTTP_201_CREATED)
def create_note(note: Note):
    for existing_note in notes_storage:
        if existing_note["id"] == note.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A note with this ID already exists."
            )

    notes_storage.append(note.model_dump())

    return {
        "message": "Note created successfully.",
        "note": note
    }


# GET: Retrieve all notes
@app.get("/notes")
def get_notes():
    return {
        "message": "Notes retrieved successfully.",
        "notes": notes_storage
    }


# GET: Retrieve a note by ID
@app.get("/notes/{note_id}")
def get_note(note_id: int):
    if note_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID. ID must be greater than zero."
        )

    for note in notes_storage:
        if note["id"] == note_id:
            return note

    raise note_not_found()


# PUT: Update a note by ID
@app.put("/notes/{note_id}")
def update_note(note_id: int, updated_note: Note):
    if note_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID. ID must be greater than zero."
        )

    for index, note in enumerate(notes_storage):
        if note["id"] == note_id:
            if updated_note.id != note_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The note ID in the request body must match the URL ID."
                )

            notes_storage[index] = updated_note.model_dump()

            return {
                "message": "Note updated successfully.",
                "note": updated_note
            }

    raise note_not_found()


# DELETE: Delete a note by ID
@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    if note_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid note ID. ID must be greater than zero."
        )

    for index, note in enumerate(notes_storage):
        if note["id"] == note_id:
            deleted_note = notes_storage.pop(index)

            return {
                "message": "Note deleted successfully.",
                "note": deleted_note
            }

    raise note_not_found()

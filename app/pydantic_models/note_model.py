from pydantic import BaseModel

class Note(BaseModel):
    title: str
    description: str

class NoteComment(BaseModel):
    description: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "description": "Very interesting comment"
                }
            ]
        }
    }

class FavoriteNote(BaseModel):
    id: int

    user_id: int
    note_id: int

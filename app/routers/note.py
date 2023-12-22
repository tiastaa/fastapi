from typing import Annotated

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.pydantic_models.note_model import Note, NoteComment
from app.models.note_models import Notes, NoteComments, FavoriteNotes
from app.routers.auth import get_current_user

from app.session import get_session
from app.models.users import Users

note_router = APIRouter(prefix='/note', tags=['notes'])

db_dependency = Annotated[Session, Depends(get_session)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@note_router.get('/get_all')
def get_notes(db_session: db_dependency):
    notes = db_session.query(Notes).all()
    return notes

@note_router.get('/get_by_id')
def get_note_by_id(db_session: db_dependency, id):
    note = db_session.query(Notes).filter(Notes.id == id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such note in db')
    return note


@note_router.post('/create_note')
async def create_note(db_session: db_dependency, item: Note, user: user_dependency):
    user_id = user[1]
    new_note = Notes(user_id=user_id, title=item.title, description=item.description)
    db_session.add(new_note)
    db_session.commit()
    return new_note

@note_router.put('/update_note')
async def update_note(note_id, item: Note, db_session: db_dependency, user: user_dependency):
    user_id = user[1]
    user = db_session.query(Users).filter(Users.id == user_id).first()
    note = db_session.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such note')
    if note.user_id == user_id or user.is_admin > 0:
        note.title = item.title
        note.description = item.description
        db_session.commit()
        return note
    raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail='You are a teapot')


@note_router.delete('/delete_note')
async def delete_note(note_id, db_session: db_dependency, user: user_dependency):
    user_id = user[1]
    user = db_session.query(Users).filter(Users.id == user_id).first()
    note = db_session.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such note')
    if note.user_id == user_id or user.is_admin > 0:
        db_session.query(Notes).filter(Notes.id == note_id).delete()
        db_session.commit()
        return note
    raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail='You are a teapot')


@note_router.post('/favorite_note')
def favorite_note(note_id, db_session: db_dependency, user: user_dependency):
    user_id = user[1]
    query = db_session.query(FavoriteNotes).filter(FavoriteNotes.note_id == note_id, FavoriteNotes.user_id == user_id)
    note = db_session.query(Notes).filter(Notes.id == note_id).first()
    if query.first():
        query.delete()
        note.favorites -= 1
        db_session.commit()
        return "Unfavored"

    new_favorite = FavoriteNotes(note_id=note_id, user_id=user_id)
    note.favorites += 1
    db_session.add(new_favorite)
    db_session.commit()
    return "Favored"

@note_router.post('/create_note-comment')
async def create_comment(db_session: db_dependency, item: NoteComment, user: user_dependency, note_id):
    user_id = user[1]
    note = db_session.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such note')
    new_comment = NoteComments(user_id=user_id, description=item.description, note_id=note_id)
    note.note_comments += 1
    db_session.add(new_comment)
    db_session.commit()
    return new_comment

@note_router.put('/update_note-comment')
async def update_comment(id, note_id, item: NoteComment, db_session: db_dependency, user: user_dependency):
    user_id = user[1]
    note = db_session.query(Notes).filter(Notes.id == note_id).first()
    comment = db_session.query(NoteComments).filter(NoteComments.id == id).first()
    user = db_session.query(Users).filter(Users.id == user_id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such note')
    
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such comment')
    
    if comment.note_id != note.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such comment in note')
    
    if comment.user_id == user_id or user.is_admin > 0:
        comment.description = item.description
        db_session.commit()
        return comment
    raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail='You are a teapot')

@note_router.delete('/delete_note-comment')
async def delete_comment(id, note_id, db_session: db_dependency, user: user_dependency):
    user_id = user[1]
    note = db_session.query(Notes).filter(Notes.id == note_id).first()
    user = db_session.query(Users).filter(Users.id == user_id).first()
    comment = db_session.query(NoteComments).filter(NoteComments.id == id).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such comment')
    if note.id != note_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No such comment in note')
    if comment.user_id == user_id or user.is_admin > 0:
        db_session.query(NoteComments).filter(NoteComments.id == id).delete()
        db_session.commit()
        return note
    raise HTTPException(status_code=status.HTTP_418_IM_A_TEAPOT, detail='You are a teapot')


from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.session import Base


class Notes(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    favorites = Column(Integer, default=0)
    note_comments = Column(Integer, default=0)
    abc = Column(String(20), nullable=True)


class NoteComments(Base):
    __tablename__ = 'note-comments'

    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    note_id = Column(Integer, ForeignKey('notes.id'), nullable=False)

class FavoriteNotes(Base):
    __tablename__ = 'favorites'
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    note_id = Column(Integer, ForeignKey('notes.id'), nullable=False)
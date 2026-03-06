from sqlalchemy import Column, Integer, String, Float, Text, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    bgg_id = Column(Integer, unique=True, index=True)
    title = Column(String, index=True)
    year_published = Column(Integer)
    min_players = Column(Integer)
    max_players = Column(Integer)
    play_time = Column(Integer)
    complexity = Column(Float)
    avg_rating = Column(Float)
    mechanics = Column(Text)   # stored as comma-separated string
    categories = Column(Text)

class Collection(Base):
    __tablename__ = "collection"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, index=True)
    status = Column(String)    # owned / wishlist / played
    personal_rating = Column(Float, nullable=True)
    play_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
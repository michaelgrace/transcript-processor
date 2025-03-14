import os
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import datetime

load_dotenv()

# Get database path from environment variables
DB_PATH = os.getenv("DB_PATH", "./data/transcripts.db")

# Create database directory if it doesn't exist
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Create engine and base
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
Base = declarative_base()

# Define Transcript model
class Transcript(Base):
    __tablename__ = "transcripts"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_content = Column(Text, nullable=False)
    processed_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    format_style = Column(String(50), default="Article")
    
    def __repr__(self):
        return f"<Transcript(id={self.id}, filename='{self.filename}')>"

# Create tables
Base.metadata.create_all(engine)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

def save_transcript(filename, original_content, processed_content, format_style="Article"):
    """Save a transcript to the database"""
    transcript = Transcript(
        filename=filename,
        original_content=original_content,
        processed_content=processed_content,
        format_style=format_style
    )
    session.add(transcript)
    session.commit()
    return transcript.id

def get_transcript(transcript_id):
    """Get a transcript by ID"""
    return session.query(Transcript).filter(Transcript.id == transcript_id).first()

def get_all_transcripts():
    """Get all transcripts"""
    return session.query(Transcript).order_by(Transcript.created_at.desc()).all()

def delete_transcript(transcript_id):
    """Delete a transcript from the database by ID"""
    session = Session()
    try:
        transcript = session.query(Transcript).filter(Transcript.id == transcript_id).first()
        if transcript:
            session.delete(transcript)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting transcript: {e}")
        return False
    finally:
        session.close()
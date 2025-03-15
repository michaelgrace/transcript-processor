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

def save_post_ideas(transcript_id, post_ideas_content):
    """Save post ideas associated with a transcript"""
    conn = None  # Initialize conn to None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if we need to create the post_ideas table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_ideas (
            id INTEGER PRIMARY KEY,
            transcript_id INTEGER,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (transcript_id) REFERENCES transcripts(id)
        )
        ''')
        
        # Check if post ideas already exist for this transcript
        cursor.execute("SELECT id FROM post_ideas WHERE transcript_id = ?", (transcript_id,))
        existing_id = cursor.fetchone()
        
        if existing_id:
            # Update existing post ideas
            cursor.execute("UPDATE post_ideas SET content = ? WHERE transcript_id = ?", 
                           (post_ideas_content, transcript_id))
            post_id = existing_id[0]
        else:
            # Insert new post ideas
            cursor.execute("INSERT INTO post_ideas (transcript_id, content) VALUES (?, ?)", 
                           (transcript_id, post_ideas_content))
            post_id = cursor.lastrowid
        
        conn.commit()
        return post_id
    except Exception as e:
        print(f"Error saving post ideas: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_post_ideas(transcript_id):
    """Retrieve post ideas for a specific transcript"""
    conn = None  # Initialize conn to None before the try block
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, content FROM post_ideas WHERE transcript_id = ?", (transcript_id,))
        result = cursor.fetchone()
        
        if result:
            return {"id": result[0], "content": result[1]}
        else:
            return None
    except Exception as e:
        print(f"Error retrieving post ideas: {e}")
        return None
    finally:
        if conn:  # Now this check is safe
            conn.close()

def delete_post_ideas(transcript_id):
    """Delete post ideas for a specific transcript"""
    conn = None  # Initialize conn to None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM post_ideas WHERE transcript_id = ?", (transcript_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting post ideas: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_connection():
    """Get a SQLite connection"""
    return sqlite3.connect(DB_PATH)
import os
import datetime
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Get database connection details from environment variables
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "transcripts")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_connection():
    """Get a database connection"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

def save_transcript(filename, original_content, processed_content, format_style):
    """Save a transcript to the database"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transcripts (filename, original_content, processed_content, format_style) VALUES (%s, %s, %s, %s) RETURNING id",
            (filename, original_content, processed_content, format_style)
        )
        transcript_id = cursor.fetchone()[0]
        conn.commit()
        return transcript_id
    except Exception as e:
        print(f"Error saving transcript: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()

def get_transcript(transcript_id):
    """Retrieve a transcript by ID"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, original_content, processed_content, format_style FROM transcripts WHERE id = %s", (transcript_id,))
        result = cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "filename": result[1],
                "original_content": result[2],
                "processed_content": result[3],
                "format_style": result[4]
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_transcripts():
    """Retrieve all transcripts"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, original_content, processed_content, format_style FROM transcripts ORDER BY created_at DESC")
        transcripts = cursor.fetchall()
        return [
            {
                "id": t[0],
                "filename": t[1],
                "original_content": t[2],
                "processed_content": t[3],
                "format_style": t[4]
            }
            for t in transcripts
        ]
    except Exception as e:
        print(f"Error retrieving all transcripts: {e}")
        return []
    finally:
        if conn:
            conn.close()

def delete_transcript(transcript_id):
    """Delete a transcript by ID"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transcripts WHERE id = %s", (transcript_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting transcript: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def save_post_ideas(transcript_id, content):
    """Save post ideas for a transcript"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO post_ideas (transcript_id, content) VALUES (%s, %s) ON CONFLICT (transcript_id) DO UPDATE SET content = %s",
            (transcript_id, content, content)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving post ideas: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_post_ideas(transcript_id):
    """Retrieve post ideas for a transcript"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM post_ideas WHERE transcript_id = %s", (transcript_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print(f"Error retrieving post ideas: {e}")
        return None
    finally:
        if conn:
            conn.close()

def delete_post_ideas(transcript_id):
    """Delete post ideas for a transcript"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM post_ideas WHERE transcript_id = %s", (transcript_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting post ideas: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def save_rewrite(transcript_id, content, options):
    """Save a rewritten transcript version to the database"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        options_str = ",".join(options)
        cursor.execute(
            "INSERT INTO rewrites (transcript_id, content, options) VALUES (%s, %s, %s) ON CONFLICT (transcript_id) DO UPDATE SET content = %s, options = %s",
            (transcript_id, content, options_str, content, options_str)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving rewrite: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_rewrite(transcript_id):
    """Retrieve a rewritten transcript"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content, options FROM rewrites WHERE transcript_id = %s", (transcript_id,))
        result = cursor.fetchone()
        if result:
            content, options_str = result
            options = options_str.split(",") if options_str else []
            return {"content": content, "options": options}
        else:
            return None
    except Exception as e:
        print(f"Error retrieving rewrite: {e}")
        return None
    finally:
        if conn:
            conn.close()

def delete_rewrite(transcript_id):
    """Delete a rewritten transcript"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rewrites WHERE transcript_id = %s", (transcript_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting rewrite: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def save_transcript_metadata(transcript_id, metadata):
    """Save transcript metadata to the database"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        topics = json.dumps(metadata.get("topics", []))
        keywords = json.dumps(metadata.get("keywords", []))
        sentiment = json.dumps(metadata.get("sentiment", {}))
        tags = json.dumps(metadata.get("tags", []))
        cursor.execute(
            """
            INSERT INTO transcript_metadata (transcript_id, topics, keywords, sentiment, tags)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (transcript_id) DO UPDATE
            SET topics = %s, keywords = %s, sentiment = %s, tags = %s
            """,
            (transcript_id, topics, keywords, sentiment, tags, topics, keywords, sentiment, tags),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving transcript metadata: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_transcript_metadata(transcript_id):
    """Retrieve transcript metadata by ID"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT topics, keywords, sentiment, tags FROM transcript_metadata WHERE transcript_id = %s",
            (transcript_id,),
        )
        result = cursor.fetchone()
        if result:
            topics, keywords, sentiment, tags = result
            topics = json.loads(topics) if topics else []
            keywords = json.loads(keywords) if keywords else []
            sentiment = json.loads(sentiment) if sentiment else {}
            tags = json.loads(tags) if tags else []
            return {
                "topics": topics,
                "keywords": keywords,
                "sentiment": sentiment,
                "tags": tags,
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving transcript metadata: {e}")
        return None
    finally:
        if conn:
            conn.close()

def log_analytics_event(transcript_id, action_type, details=None):
    """Log an analytics event"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        action_details = json.dumps(details) if details else '{}'
        cursor.execute(
            """
            INSERT INTO analytics (transcript_id, action_type, action_details)
            VALUES (%s, %s, %s)
            """,
            (transcript_id, action_type, action_details),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error logging analytics: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_analytics_summary():
    """Get summary analytics data"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Popular rewrite options
        cursor.execute("""
            SELECT 
                action_details->>'options' as options,
                COUNT(*) as count
            FROM analytics
            WHERE action_type = 'rewrite' AND action_details->>'options' IS NOT NULL
            GROUP BY action_details->>'options'
            ORDER BY count DESC
            LIMIT 5
        """)
        popular_options = cursor.fetchall()
        
        # Popular format styles
        cursor.execute("""
            SELECT 
                action_details->>'format_style' as format_style,
                COUNT(*) as count
            FROM analytics
            WHERE action_type = 'format' AND action_details->>'format_style' IS NOT NULL
            GROUP BY action_details->>'format_style'
            ORDER BY count DESC
        """)
        popular_formats = cursor.fetchall()
        
        # Action counts by type
        cursor.execute("""
            SELECT 
                action_type,
                COUNT(*) as count
            FROM analytics
            GROUP BY action_type
            ORDER BY count DESC
        """)
        action_counts = cursor.fetchall()
        
        return {
            "popular_options": popular_options,
            "popular_formats": popular_formats,
            "action_counts": action_counts
        }
    except Exception as e:
        print(f"Error retrieving analytics: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def ensure_tables_exist():
    """Create all required tables if they don't exist"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create transcripts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                original_content TEXT NOT NULL,
                processed_content TEXT NOT NULL,
                format_style VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create post_ideas table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS post_ideas (
                transcript_id INTEGER PRIMARY KEY REFERENCES transcripts(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create rewrites table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rewrites (
                transcript_id INTEGER PRIMARY KEY REFERENCES transcripts(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                options TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                transcript_id INTEGER REFERENCES transcripts(id) ON DELETE CASCADE,
                action_type VARCHAR(50) NOT NULL,
                action_details JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create transcript_metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcript_metadata (
                transcript_id INTEGER PRIMARY KEY REFERENCES transcripts(id) ON DELETE CASCADE,
                topics JSONB,
                keywords JSONB,
                sentiment JSONB,
                tags JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("All required tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()
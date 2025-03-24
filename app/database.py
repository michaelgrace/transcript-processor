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

def save_transcript(filename, original_content, processed_content, format_style, source_type="transcript"):
    """Save a transcript to the database"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transcripts (filename, original_content, processed_content, format_style, source_type) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (filename, original_content, processed_content, format_style, source_type)
        )
        transcript_id = cursor.fetchone()[0]
        conn.commit()
        return transcript_id
    except Exception as e:
        print(f"Error saving transcript: {e}")
        import traceback
        print(traceback.format_exc())  # Add this to get detailed error info
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
    """Save post ideas to the database"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Debug print to verify content
        print(f"DEBUG: Saving post ideas. Content type: {type(content)}, length: {len(content)}")
        
        # Check if post ideas already exist for this transcript
        cursor.execute(
            "SELECT id FROM post_ideas WHERE transcript_id = %s",
            (transcript_id,)
        )
        result = cursor.fetchone()
        
        if result:
            # Update existing post ideas
            cursor.execute(
                "UPDATE post_ideas SET content = %s, created_at = CURRENT_TIMESTAMP WHERE transcript_id = %s",
                (content, transcript_id)
            )
        else:
            # Insert new post ideas
            cursor.execute(
                "INSERT INTO post_ideas (transcript_id, content) VALUES (%s, %s)",
                (transcript_id, content)
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
    """Get post ideas for a transcript"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT content FROM post_ideas WHERE transcript_id = %s",
            (transcript_id,)
        )
        result = cursor.fetchone()
        # Return just the content string, not the whole tuple
        return result[0] if result else None
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
        options_str = ",".join(options) if isinstance(options, list) else options
        
        # First, check if a rewrite exists for this transcript
        cursor.execute("SELECT id FROM rewrites WHERE transcript_id = %s", (transcript_id,))
        existing_rewrite = cursor.fetchone()
        
        if existing_rewrite:
            # Update existing rewrite
            cursor.execute(
                "UPDATE rewrites SET content = %s, options = %s WHERE transcript_id = %s",
                (content, options_str, transcript_id)
            )
        else:
            # Insert new rewrite
            cursor.execute(
                "INSERT INTO rewrites (transcript_id, content, options) VALUES (%s, %s, %s)",
                (transcript_id, content, options_str)
            )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving rewrite: {e}")
        import traceback
        print(traceback.format_exc())
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
        
        # Convert Python objects to JSON strings
        topics = json.dumps(metadata.get("topics", []))
        keywords = json.dumps(metadata.get("keywords", []))
        sentiment = json.dumps(metadata.get("sentiment", {}))
        tags = json.dumps(metadata.get("tags", []))
        
        cursor.execute(
            """
            INSERT INTO transcript_metadata (transcript_id, topics, keywords, sentiment, tags)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (transcript_id) DO UPDATE
            SET topics = EXCLUDED.topics, 
                keywords = EXCLUDED.keywords, 
                sentiment = EXCLUDED.sentiment, 
                tags = EXCLUDED.tags
            """,
            (transcript_id, topics, keywords, sentiment, tags)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving transcript metadata: {e}")
        import traceback
        print(traceback.format_exc())
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
            
            # More robust handling of JSON parsing
            try:
                topics = json.loads(topics) if isinstance(topics, str) else (topics or [])
                keywords = json.loads(keywords) if isinstance(keywords, str) else (keywords or [])
                sentiment = json.loads(sentiment) if isinstance(sentiment, str) else (sentiment or {})
                tags = json.loads(tags) if isinstance(tags, str) else (tags or [])
            except json.JSONDecodeError as e:
                print(f"JSON decode error in metadata: {e}")
                # Provide default values if JSON parsing fails
                topics = topics if isinstance(topics, list) else []
                keywords = keywords if isinstance(keywords, list) else []
                sentiment = sentiment if isinstance(sentiment, dict) else {}
                tags = tags if isinstance(tags, list) else []
            
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
        import traceback
        print(traceback.format_exc())  # Add full traceback
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
        
        # Popular rewrite options - Use unnest to handle comma-separated values
        cursor.execute("""
            WITH option_values AS (
                SELECT 
                    transcript_id, 
                    regexp_split_to_table(action_details->>'options', ',') AS option_value
                FROM analytics
                WHERE action_type = 'rewrite' AND action_details->>'options' IS NOT NULL
            )
            SELECT 
                option_value AS "Options",
                COUNT(*) AS "Count"
            FROM option_values
            GROUP BY option_value
            ORDER BY "Count" DESC
            LIMIT 10
        """)
        popular_options = cursor.fetchall()
        
        # Popular format styles
        cursor.execute("""
            SELECT 
                action_details->>'format_style' AS "Format",
                COUNT(*) AS "Count"
            FROM analytics
            WHERE action_type = 'format' AND action_details->>'format_style' IS NOT NULL
            GROUP BY action_details->>'format_style'
            ORDER BY "Count" DESC
        """)
        popular_formats = cursor.fetchall()
        
        # Action counts by type - ensure column names are correct
        cursor.execute("""
            SELECT 
                COALESCE(action_type, 'unknown') as action_type,  -- Ensure no NULL values
                COUNT(*) as count
            FROM analytics
            GROUP BY action_type
            ORDER BY count DESC
        """)
        action_counts = cursor.fetchall()

        # Print for debugging
        print("Action counts from database:", action_counts)
        
        # Get common topics from metadata
        cursor.execute("""
            WITH topic_values AS (
                SELECT jsonb_array_elements_text(topics) as topic
                FROM transcript_metadata
                WHERE topics IS NOT NULL
            )
            SELECT 
                topic AS "Topic",
                COUNT(*) AS "Count"
            FROM topic_values
            GROUP BY topic
            ORDER BY "Count" DESC
            LIMIT 10
        """)
        common_topics = cursor.fetchall()
        
        # Get sentiment distribution
        cursor.execute("""
            WITH sentiment_values AS (
                SELECT 
                    sentiment->>'classification' as sentiment_type
                FROM transcript_metadata
                WHERE sentiment IS NOT NULL AND sentiment->>'classification' IS NOT NULL
            )
            SELECT 
                COALESCE(sentiment_type, 'neutral') AS "Sentiment",
                COUNT(*) AS "Count"
            FROM sentiment_values
            GROUP BY sentiment_type
            ORDER BY "Count" DESC
        """)
        sentiment_distribution = cursor.fetchall()
        
        # Return all data
        return {
            "popular_options": popular_options,
            "popular_formats": popular_formats,
            "action_counts": action_counts,
            "common_topics": common_topics,
            "sentiment_distribution": sentiment_distribution
        }
    except Exception as e:
        print(f"Error retrieving analytics: {e}")
        import traceback
        print(traceback.format_exc())
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
                source_type VARCHAR(50) DEFAULT 'transcript',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if source_type column exists, add if it doesn't
        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='transcripts' AND column_name='source_type'
            """)
            has_column = cursor.fetchone() is not None
            
            if not has_column:
                cursor.execute("ALTER TABLE transcripts ADD COLUMN source_type VARCHAR(50) DEFAULT 'transcript'")
                conn.commit()
                print("Added source_type column to transcripts table")
        except Exception as e:
            print(f"Error checking/adding source_type column: {e}")
            conn.rollback()
        
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
                id SERIAL PRIMARY KEY,  -- This is the primary key, not transcript_id
                transcript_id INTEGER REFERENCES transcripts(id) ON DELETE CASCADE,
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
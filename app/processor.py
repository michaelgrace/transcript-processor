import os
import re
import pysrt
from dotenv import load_dotenv
import openai  # Import the module, not the class
import streamlit as st

load_dotenv()

# Configure OpenAI with the older style
openai.api_key = os.getenv("API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4")

def process_srt(content, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True, format_style="Article"):
    """Process SRT file content"""
    try:
        # Parse SRT content
        subs = pysrt.from_string(content)
        
        # Extract text without timestamps
        text = ' '.join([sub.text for sub in subs])
        
        # Remove HTML tags if any
        text = re.sub(r'<.*?>', '', text)
        
        return format_text(text, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style)
    except Exception as e:
        print(f"SRT processing error: {e}")
        # If SRT parsing fails, treat as plain text
        return format_text(content, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style)

def process_text(content, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True, format_style="Article"):
    """Process plain text file content"""
    return format_text(content, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style)

def format_text(text, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True, format_style="Article"):
    """Format text using AI to add proper structure with detailed instructions"""
    try:
        system_prompt = """You are an expert in natural language processing and document formatting. Your task is to transform spoken word transcripts into well-structured text while preserving the natural flow of speech.

1. Natural Language Analysis:
   - Identify complete thoughts and ideas
   - Recognize natural speech patterns and pauses
   - Detect topic transitions
   - Understand speaker's rhythm and flow

2. Formatting Instructions:
   - Create proper sentences that maintain the speaker's natural cadence
   - Group related ideas into coherent paragraphs
   - Add clear topic headings that reflect the content
   - Use markdown for structure (## for headings)
   - Add bullet points (*) for lists or emphasized points

3. Specific Requirements:
   - End sentences at natural pauses and complete thoughts
   - Start new paragraphs when topics shift
   - Preserve the speaker's original words and meaning
   - Remove unnecessary periods and fix punctuation
   - Maintain the conversational tone while improving readability

4. CRITICAL RULES:
   - Preserve ALL original content
   - Keep the speaker's authentic voice
   - Don't summarize or remove anything
   - Don't add interpretations or new content
   - Focus on structure and readability only"""

        print(f"Using model: {AI_MODEL}")
        
        # Use the older API format that's compatible with openai==0.28.0
        response = openai.ChatCompletion.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "This is a spoken word transcript that needs to be formatted into clear sentences and paragraphs while preserving the natural flow of speech. Format this text:\n\n" + text}
            ],
            temperature=0.3,
            max_tokens=4096
        )
        
        # Extract the response content using the older format
        formatted_text = response.choices[0].message["content"]
        
        if not formatted_text.strip():
            raise ValueError("AI returned empty response")
            
        return formatted_text
        
    except Exception as e:
        error_message = f"❌ AI FORMATTING ERROR: {str(e)}"
        print(error_message)
        st.error(error_message)
        return f"Error processing with AI: {str(e)}\n\nOriginal text:\n{text}"

def detect_and_process(file_content, filename, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True, format_style="Article"):
    """Detect file type and process accordingly with formatting options"""
    if filename.lower().endswith('.srt'):
        return process_srt(file_content, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style)
    else:
        return process_text(file_content, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style)
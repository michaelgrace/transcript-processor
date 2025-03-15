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
    """Format text using OpenAI API"""
    
    # Build the system prompt based on formatting options
    system_instructions = [
        "You are an expert transcript formatter and editor.",
        "Your task is to improve the readability of transcripts while maintaining their original meaning."
    ]
    
    # Add specific formatting instructions based on user selections
    if add_paragraphs:
        system_instructions.append("Organize the content into clear, logical paragraphs based on topic changes or natural breaks in conversation.")
    
    if add_headings:
        system_instructions.append("Insert appropriate section headings (using markdown # syntax) to highlight main topics and improve document structure.")
    
    if fix_grammar:
        system_instructions.append("Fix grammar, punctuation, and sentence structure while preserving the original meaning.")
    else:
        system_instructions.append("Maintain the original grammar and sentence structure.")
    
    if highlight_key_points:
        system_instructions.append("Highlight key points, important concepts, or conclusions using **bold** markdown formatting.")
    
    # Add style-specific formatting instructions
    if format_style == "Article":
        system_instructions.append("Format the text as a polished article with a clear introduction, body, and conclusion.")
        system_instructions.append("Use a professional, journalistic tone.")
    elif format_style == "Transcript":
        system_instructions.append("Maintain the conversational back-and-forth nature of the transcript.")
        system_instructions.append("Clearly indicate speaker changes with bold formatting (e.g., **Speaker 1:**).")
    elif format_style == "Meeting Notes":
        system_instructions.append("Format as concise meeting notes with clear action items and decisions.")
        system_instructions.append("Use bullet points for lists and action items.")
        system_instructions.append("Summarize discussions rather than including all dialogue.")
    elif format_style == "Academic":
        system_instructions.append("Format with a formal academic style, using appropriate scholarly language.")
        system_instructions.append("Organize with clear thesis statements and supporting evidence.")
        system_instructions.append("Use numbered sections for different topics or arguments.")
    
    system_prompt = "\n".join(system_instructions)
    
    try:
        response = openai.ChatCompletion.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please format this transcript:\n\n{text}"}
            ],
            temperature=0.3  # Lower temperature for more consistent formatting
        )
        
        formatted_text = response.choices[0].message["content"]
        return formatted_text
    except Exception as e:
        print(f"Error formatting text: {e}")
        return text  # Return original text if formatting fails

def detect_and_process(file_content, filename, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True, format_style="Article"):
    """Detect file type and process accordingly with formatting options"""
    if filename.lower().endswith('.srt'):
        return process_srt(file_content, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style)
    else:
        return process_text(file_content, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style)

def generate_post_ideas(transcript_content):
    """Generate content ideas for social media posts based on a transcript"""
    try:
        system_prompt = """You are an expert content creator specializing in helping creators repurpose their content across platforms. 
        Your task is to analyze a transcript and generate creative ideas for social media posts and videos.

        Based on the provided transcript, generate the following:

        1. YouTube Titles: Compelling and intriguing video titles.
        2. Curiosity Hooks: Engaging opening lines to capture attention.
        3. Thumbnail Concepts: Ideas with clear text and imagery for easy visualization.
        4. Search Questions: Possible viewer queries that might lead them to the video.
        5. Viewer Problems: Potential issues viewers are trying to solve when they find the video.
        6. Related Topics: Subjects relevant to the video's theme.

        If the transcript is lengthy, generate 5 ideas for each category.
        If the transcript is short, generate at least 3 ideas for each category.

        Format your answer with clear headings using markdown.
        """

        # Check length of transcript to determine how many ideas to generate
        is_short = len(transcript_content.split()) < 300  # Arbitrary threshold for "short" transcript
        
        user_prompt = f"The following is a transcript of content. Please analyze it and generate content ideas:\n\n{transcript_content}"
        if is_short:
            user_prompt += "\n\nThis transcript is relatively short, so please generate at least 3 ideas for each category."
        else:
            user_prompt += "\n\nThis transcript is substantial, so please generate at least 5 ideas for each category."

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,  # Higher temperature for more creativity
            max_tokens=2048
        )
        
        # Extract the response content
        ideas = response.choices[0].message["content"]
        
        if not ideas.strip():
            raise ValueError("AI returned empty response")
            
        return ideas
        
    except Exception as e:
        error_message = f"❌ POST IDEAS GENERATION ERROR: {str(e)}"
        print(error_message)
        st.error(error_message)
        return f"Error generating post ideas: {str(e)}"
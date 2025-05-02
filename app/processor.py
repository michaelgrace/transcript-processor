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

def process_srt(content, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True, format_style="Article", rewrite_options=None):
    """Process SRT file content"""
    try:
        # Parse SRT content
        subs = pysrt.from_string(content)
        
        # Extract text without timestamps
        text = ' '.join([sub.text for sub in subs])
        
        # Remove HTML tags if any
        text = re.sub(r'<.*?>', '', text)
        
        return format_text(text, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style, rewrite_options)
    except Exception as e:
        print(f"SRT processing error: {e}")
        # If SRT parsing fails, treat as plain text
        return format_text(content, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style, rewrite_options)

def process_text(content, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True, format_style="Article", rewrite_options=None):
    """Process plain text file content"""
    return format_text(content, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style, rewrite_options)

def format_text(
    text, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True,
    format_style="Article", rewrite_options=None
):
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
    else:
        # Explicitly instruct the model NOT to add headings
        system_instructions.append("Do not add any headings or section titles. Do not use markdown # syntax or similar heading formatting. Only use plain text or paragraphs.")

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
    
    # Add rewrite options to system prompt
    if rewrite_options:
        for opt in rewrite_options:
            opt_lc = opt.lower().replace(" ", "_")
            if opt_lc == "clear_&_simple" or opt_lc == "clear_simple":
                system_instructions.append("Use clear, confident language suitable for an 8th-grade reading level. Be authoritative but avoid overly complex vocabulary or jargon.")
            elif opt_lc == "professional":
                system_instructions.append("Use a balanced, measured tone appropriate for business contexts. Be precise and thoughtful, avoiding filler language.")
            elif opt_lc == "storytelling":
                system_instructions.append("Reshape the content into a narrative flow with a clear beginning, middle, and end. Use descriptive language and transitional phrases.")
            elif opt_lc == "youtube_script":
                system_instructions.append("Structure the content as an engaging video script with clear sections. Use conversational cues and format with intro, body, and conclusion.")
            elif opt_lc == "educational":
                system_instructions.append("Present information in a structured, easy-to-follow format that facilitates learning. Include examples and analogies.")
            elif opt_lc == "balanced":
                system_instructions.append("Use a mature but approachable tone that connects with the reader. Balance friendliness with substance.")
            elif opt_lc == "shorter":
                system_instructions.append("Reduce the word count by approximately 25% while preserving all key information. Focus on concise phrasing.")
            elif opt_lc == "longer":
                system_instructions.append("Expand the content by approximately 25% with additional context, examples, and detail.")
    
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

def detect_and_process(
    content, filename, add_paragraphs=True, add_headings=True, fix_grammar=True, highlight_key_points=True,
    format_style="Article", is_binary=False, rewrite_options=None
):
    """
    Detect file type and process accordingly
    If is_binary is True, content is treated as binary data (for PDF files)
    """
    import os
    
    file_extension = os.path.splitext(filename)[1].lower()
    processed_content = ""
    
    # Handle PDF files
    if file_extension == '.pdf' and is_binary:
        # Extract text from PDF
        content = extract_text_from_pdf(content)
        # Process the extracted text
        processed_content = format_text(
            content, 
            add_paragraphs=add_paragraphs,
            add_headings=add_headings,
            fix_grammar=fix_grammar,
            highlight_key_points=highlight_key_points,
            format_style=format_style,
            rewrite_options=rewrite_options
        )
    # Process SRT files
    elif file_extension == '.srt':
        # Process the SRT file directly - process_srt already calls format_text internally
        processed_content = process_srt(
            content,
            add_paragraphs=add_paragraphs,
            add_headings=add_headings,
            fix_grammar=fix_grammar,
            highlight_key_points=highlight_key_points,
            format_style=format_style,
            rewrite_options=rewrite_options
        )
    # Process other text files
    else:
        # Process plain text
        processed_content = format_text(
            content, 
            add_paragraphs=add_paragraphs,
            add_headings=add_headings,
            fix_grammar=fix_grammar,
            highlight_key_points=highlight_key_points,
            format_style=format_style,
            rewrite_options=rewrite_options
        )
    
    # Adjust heading sizes as the final step
    processed_content = adjust_markdown_headings(processed_content)
    
    return processed_content

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

def rewrite_transcript(content, options):
    """
    Rewrite a transcript based on selected style options
    
    Args:
        content (str): The transcript content to rewrite
        options (list): List of selected style options
            - "clear_simple" - Clear language at 8th grade level
            - "professional" - Business appropriate tone
            - "storytelling" - Narrative structure with flow
            - "youtube_script" - Structured for video
            - "educational" - Explains concepts clearly
            - "balanced" - Mature but approachable
            - "shorter" - Reduce word count by ~25%
            - "longer" - Expand content by ~25%
    
    Returns:
        str: The rewritten transcript
    """
    
    # Validate options
    if "shorter" in options and "longer" in options:
        return "ERROR: Cannot select both 'Shorter' and 'Longer' options. Please choose only one."
    
    # Word and phrase blacklist
    blacklisted_terms = [
        "realm",
        "delve", 
        "dive deep",
        "dive into",
        "dive in",
        "journey",
        "explore",  
        "Welcome to our exploration",   
        "Welcome to our journey",
        "Welcome to our deep dive", 
        "Welcome to our realm",
        "Welcome to our discussion",
        "Welcome to our analysis",
        "Welcome to our exploration",
        "Welcome to our analysis",
        "Let's explore",
        "In conclusion",                
        "What if I told you",
        "What if I said",
        "What if I shared",
        "In conclusion",        
        "In summary",
        "In closing",
        "profound"
        

    ]
    
    # Build the system prompt based on selected options
    system_instructions = [
        "You are an expert content editor specializing in rewriting and reformatting transcripts.",
        "Your task is to rewrite the provided transcript according to the specified style options while preserving the original meaning and information.",
        "",
        "IMPORTANT: You must NEVER use the following words or phrases in your rewrite:",
    ]
    
    # Add blacklisted terms to instructions
    for term in blacklisted_terms:
        system_instructions.append(f"- \"{term}\"")
    
    system_instructions.append("")
    system_instructions.append("If you feel tempted to use any of these terms, find alternative expressions instead.")
    
    # Add specific style instructions based on user selections
    if "clear_simple" in options:
        system_instructions.append("Use clear, confident language suitable for an 8th-grade reading level.")
        system_instructions.append("Be authoritative but avoid overly complex vocabulary or jargon.")
        system_instructions.append("Explain complex ideas in simple terms while maintaining accuracy.")
    
    if "professional" in options:
        system_instructions.append("Use a balanced, measured tone appropriate for business contexts.")
        system_instructions.append("Be precise and thoughtful, avoiding filler language.")
        system_instructions.append("Maintain a warm yet professional distance - neither overly formal nor casual.")
    
    if "storytelling" in options:
        system_instructions.append("Reshape the content into a narrative flow with a clear beginning, middle, and end.")
        system_instructions.append("Use descriptive language and transitional phrases to guide the reader.")
        system_instructions.append("Create a sense of progression and purpose throughout the text.")
    
    if "youtube_script" in options:
        system_instructions.append("Structure the content as an engaging video script with clear sections.")
        system_instructions.append("Use conversational cues like 'as you can see' or 'let's explore' where appropriate.")
        system_instructions.append("Format with clear intro, body sections, and conclusion with call to action.")
        system_instructions.append("Include natural transitions between topics.")
    
    if "educational" in options:
        system_instructions.append("Present information in a structured, easy-to-follow format that facilitates learning.")
        system_instructions.append("Include examples and analogies to illustrate complex points.")
        system_instructions.append("Define key terms and concepts clearly.")
        system_instructions.append("Use a progressive structure that builds understanding from basic to more complex ideas.")
    
    if "balanced" in options:
        system_instructions.append("Use a mature but approachable tone that connects with the reader.")
        system_instructions.append("Balance friendliness with substance - be conversational but not casual.")
        system_instructions.append("Write as if speaking to an intelligent peer in a thoughtful discussion.")
        system_instructions.append("Use natural language without being overly informal or using slang.")
    
    if "shorter" in options:
        system_instructions.append("Reduce the word count by approximately 25% while preserving all key information.")
        system_instructions.append("Focus on concise phrasing and removing redundancies.")
        system_instructions.append("Prioritize the most important points and concepts from the original.")
    
    if "longer" in options:
        system_instructions.append("Expand the content by approximately 25% with additional context, examples, and detail.")
        system_instructions.append("Elaborate on key concepts to provide deeper understanding.")
        system_instructions.append("Add relevant background information or explanations where helpful.")
        system_instructions.append("Include additional context or implications of the content.")
    
    # Create a cohesive system prompt
    system_prompt = "\n".join(system_instructions)
    
    try:
        response = openai.ChatCompletion.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please rewrite this transcript according to the style instructions:\n\n{content}"}
            ],
            temperature=0.4  # Moderate temperature for creativity while maintaining consistency
        )
        
        rewritten_text = response.choices[0].message["content"]
        return rewritten_text
    except Exception as e:
        error_message = f"❌ REWRITE ERROR: {str(e)}"
        print(error_message)
        st.error(error_message)
        return f"Error rewriting transcript: {str(e)}"

def analyze_transcript_metadata(content):
    """
    Generate metadata about transcript content including topics, keywords, and sentiment
    """
    try:
        system_prompt = """You are an AI specializing in content analysis. 
        Analyze the provided transcript and extract the following metadata:
        
        1. Topics: Main subjects discussed in the content (max 5)
        2. Keywords: Important terms or phrases that represent key concepts (max 10)
        3. Sentiment: Overall emotional tone (positive, negative, neutral) with confidence score
        4. Tags: Categories or labels that would help classify this content (max 8)
        
        Format your response as a JSON object with these keys: topics, keywords, sentiment, tags.
        For sentiment, include both the classification and a confidence score between 0 and 1.
        """
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this transcript:\n\n{content[:8000]}"}
            ],
            temperature=0.1  # Low temperature for consistent analysis
        )
        
        # Extract and parse JSON response
        metadata_json = response.choices[0].message["content"]
        import json
        metadata = json.loads(metadata_json)
        
        return metadata
    except Exception as e:
        print(f"Error analyzing transcript metadata: {e}")
        return {
            "topics": [],
            "keywords": [],
            "sentiment": {"classification": "neutral", "confidence": 0.5},
            "tags": []
        }

def extract_text_from_pdf(pdf_content):
    """
    Extract text from a PDF file
    """
    try:
        from io import BytesIO
        import PyPDF2
        
        # Create a file-like object from the PDF content
        pdf_file = BytesIO(pdf_content)
        
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:  # Check if text extraction was successful
                text += page_text + "\n\n"
        
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return f"Error extracting text from PDF: {str(e)}"

def adjust_markdown_headings(markdown_text):
    """
    Adjust markdown headings:
    - `#` becomes `###`
    - `##` becomes `###`
    - Default heading level is `###`
    """
    lines = markdown_text.splitlines()
    adjusted_lines = []
    
    for line in lines:
        if line.startswith('# '):
            # Convert # heading to ### heading
            adjusted_lines.append(f"### {line[2:]}")
        elif line.startswith('## '):
            # Convert ## heading to ### heading
            adjusted_lines.append(f"### {line[3:]}")
        else:
            adjusted_lines.append(line)
            
    return '\n'.join(adjusted_lines)
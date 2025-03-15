import streamlit as st
import os
from processor import detect_and_process, generate_post_ideas
from database import save_transcript, get_transcript, get_all_transcripts, delete_transcript, save_post_ideas, get_post_ideas, delete_post_ideas
import markdown
import re
import time

# Configure the page with minimal padding
st.set_page_config(page_title="Transcript Processor", layout="wide")

# Enhanced CSS with stronger hiding rules for branding and subtle button styling
st.markdown("""
<style>
/* Reduce top margin for page title */
.appview-container .main .block-container {
    padding-top: 0.5rem !important;
    padding-bottom: 0.5rem !important;
}

/* Hide streamlit branding with !important */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}

/* Hide decoration elements */
.decoration {display: none !important;}

@media print {
    .streamlit-container { padding: 0 !important; }
    header, footer, .stButton, .stDownloadButton { display: none !important; }
    .main { padding: 1rem !important; }
}

/* Remove width constraints on buttons */
.stButton > button, .stDownloadButton > button {
    width: auto !important;
}

/* Remove block display */
.stButton, .stDownloadButton {
    display: inline-block !important;
    width: auto !important;
    margin-right: 1em;
}
</style>
""", unsafe_allow_html=True)

st.title("Transcript Processor")
st.write("Upload an SRT file or text transcript to convert it into a readable format.")

# Add before the "formatting options"
st.info(f"Using AI model: {os.getenv('AI_MODEL', 'Not specified')} | API Key configured: {'Yes' if os.getenv('API_KEY') else 'No'}")

# Formatting options section
with st.expander("Formatting Options", expanded=True):
    st.write("Select the formatting elements to apply:")
    col1, col2 = st.columns(2)
    
    with col1:
        add_paragraphs = st.checkbox(
            "Paragraph Structure", 
            value=True,
            help="Organize content into logical paragraphs based on topics"
        )
        add_headings = st.checkbox(
            "Add Headings for Topics", 
            value=True,
            help="Insert section headings to highlight main topics"
        )
    
    with col2:
        fix_grammar = st.checkbox(
            "Fix Grammar & Punctuation", 
            value=True,
            help="Correct grammar and punctuation while preserving meaning"
        )
        highlight_key_points = st.checkbox(
            "Highlight Key Points", 
            value=True,
            help="Bold important concepts and conclusions"
        )
    
    format_style = st.radio(
        "Document Style",
        ["Article", "Transcript", "Meeting Notes", "Academic"],
        horizontal=True,
        index=0
    )

# File upload section
uploaded_file = st.file_uploader("Choose a file", type=["srt", "txt"])

if uploaded_file is not None:
    # Read file content
    file_content = uploaded_file.read().decode("utf-8")
    
    # Create tabs for original and processed content - CHANGED ORDER HERE
    tab2, tab1 = st.tabs(["Processed Content", "Original Content"])
    
    with tab1:
        st.text_area("Original Content", file_content, height=300)
    
    with tab2:
        with st.spinner("Processing transcript... This may take a moment."):
            # Process the file with formatting options
            processed_content = detect_and_process(
                file_content, 
                uploaded_file.name,
                add_paragraphs,
                add_headings,
                fix_grammar,
                highlight_key_points,
                format_style
            )
            
            # Display processed content
            # Check if content appears to be Markdown
            if "#" in processed_content or "**" in processed_content or "*" in processed_content:
                st.markdown(processed_content)
                
                # Download button
                st.download_button(
                    "Download Markdown",
                    processed_content,
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}_formatted.md",
                    mime="text/markdown"
                )
            else:
                st.text_area("Processed Content", processed_content, height=300)
            
            # Save button
            if st.button("Save to Database"):
                transcript_id = save_transcript(
                    filename=uploaded_file.name,
                    original_content=file_content,
                    processed_content=processed_content
                )
                st.success(f"Saved transcript with ID: {transcript_id}")

# History section
st.divider()
st.subheader("Previously Processed Transcripts")

# Handle document deletion
if 'delete_transcript' in st.session_state and st.session_state.delete_transcript:
    delete_transcript(st.session_state.delete_transcript)
    st.session_state.delete_transcript = None
    st.rerun()

# Initialize session state
if 'show_ideas_tab' not in st.session_state:
    st.session_state.show_ideas_tab = {}
    
if 'generating_ideas' not in st.session_state:
    st.session_state.generating_ideas = {}

if 'post_ideas' not in st.session_state:
    st.session_state.post_ideas = {}

# Update the section that initializes the transcript state

transcripts = get_all_transcripts()
if transcripts:
    for i, transcript in enumerate(transcripts):
        delete_key = f"delete_{transcript.id}"
        ideas_key = f"ideas_{transcript.id}"
        expander_label = f"**{transcript.filename}** (ID: {transcript.id})"
        
        with st.expander(expander_label):
            # Initialize state for this transcript if needed
            if transcript.id not in st.session_state.show_ideas_tab:
                # Check if post ideas exist for this transcript in the database
                existing_ideas = get_post_ideas(transcript.id)
                
                # If ideas exist in DB, show the tab automatically
                st.session_state.show_ideas_tab[transcript.id] = existing_ideas is not None
                st.session_state.generating_ideas[transcript.id] = False
                
                # Store the ideas content in session state if available
                if existing_ideas:
                    st.session_state.post_ideas[transcript.id] = existing_ideas["content"]
            
            # Get current state
            show_ideas = st.session_state.show_ideas_tab[transcript.id]
            
            # Rest of your code...
            
            # Simplify this tab creation code
            if show_ideas:
                # Use standard order always
                processed_tab, original_tab, ideas_tab = st.tabs(["Processed", "Original", "Post Ideas"])
            else:
                processed_tab, original_tab = st.tabs(["Processed", "Original"])
            
            with original_tab:
                st.text_area("Original Content", transcript.original_content, height=200)
            
            with processed_tab:
                # Display the content appropriately without printable container
                clean_content = transcript.processed_content
                
                if "#" in clean_content or "**" in clean_content or "*" in clean_content:
                    st.markdown(clean_content)
                else:
                    st.text_area("Processed Content", clean_content, height=200)
                
                # Add download button - original styling
                st.download_button(
                    "Download Transcript",
                    clean_content,
                    file_name=f"{transcript.filename.split('.')[0]}_processed.md",
                    mime="text/markdown",
                    key=f"download_{transcript.id}"
                )
                
                # Add delete button below download with same styling
                if st.button("Delete Transcript", key=delete_key):
                    st.session_state.delete_transcript = transcript.id
                    st.rerun()
                
                # Add Post Ideas button
                if st.button("Post Ideas", key=ideas_key):
                    # Toggle the state
                    st.session_state.show_ideas_tab[transcript.id] = True
                    st.session_state.generating_ideas[transcript.id] = True
                    st.rerun()
            
            # Handle Ideas tab if activated
            if show_ideas:
                with ideas_tab:
                    # Check if we need to generate ideas or load from database
                    if st.session_state.generating_ideas[transcript.id]:
                        with st.spinner("Generating post ideas..."):
                            # Either load existing ideas or generate new ones
                            existing_ideas = get_post_ideas(transcript.id)
                            
                            if existing_ideas:
                                ideas_content = existing_ideas["content"]
                                st.session_state.post_ideas[transcript.id] = ideas_content
                            else:
                                # Generate new ideas
                                ideas_content = generate_post_ideas(clean_content)
                                st.session_state.post_ideas[transcript.id] = ideas_content
                                
                            # Reset the generating flag
                            st.session_state.generating_ideas[transcript.id] = False
                    
                    # Display ideas content
                    if transcript.id in st.session_state.post_ideas:
                        st.markdown(st.session_state.post_ideas[transcript.id])
                        
                        # Add action buttons
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Regenerate button
                            if st.button("Regenerate Ideas", key=f"regenerate_{transcript.id}"):
                                st.session_state.generating_ideas[transcript.id] = True
                                st.rerun()
                                
                        with col2:
                            # Save button
                            if st.button("Save Ideas", key=f"save_ideas_{transcript.id}"):
                                save_post_ideas(transcript.id, st.session_state.post_ideas[transcript.id])
                                st.success("Ideas saved successfully!")
                                
                        with col3:
                            # Delete button
                            if st.button("Delete Ideas", key=f"delete_ideas_{transcript.id}"):
                                success = delete_post_ideas(transcript.id)
                                if success:
                                    st.success("Ideas deleted successfully")
                                    st.session_state.post_ideas.pop(transcript.id, None)
                                    st.session_state.show_ideas_tab[transcript.id] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to delete ideas from database")
else:
    st.info("No transcripts have been processed yet.")

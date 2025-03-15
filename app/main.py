import streamlit as st
import os
from processor import detect_and_process, generate_post_ideas, rewrite_transcript
from database import (
    save_transcript, get_transcript, get_all_transcripts, delete_transcript, 
    save_post_ideas, get_post_ideas, delete_post_ideas,
    save_rewrite, get_rewrite, delete_rewrite
)
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
    padding-top: .5rem !important;
    padding-bottom: .5rem !important;
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

/* Fix multiselect width */
div[data-testid="stMultiSelect"] {
    min-width: 200px !important;
    max-width: 400px !important;
    display: inline-block !important;
}

/* Fix button columns and alignment */
.stButton {
    text-align: left !important;
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

# Initialize session state
if 'show_ideas_tab' not in st.session_state:
    st.session_state.show_ideas_tab = {}
    
if 'generating_ideas' not in st.session_state:
    st.session_state.generating_ideas = {}

if 'post_ideas' not in st.session_state:
    st.session_state.post_ideas = {}

# New session state variables for rewrite feature
if 'show_rewrite_tab' not in st.session_state:
    st.session_state.show_rewrite_tab = {}
    
if 'generating_rewrite' not in st.session_state:
    st.session_state.generating_rewrite = {}

if 'rewrite_content' not in st.session_state:
    st.session_state.rewrite_content = {}

if 'rewrite_options' not in st.session_state:
    st.session_state.rewrite_options = {}

# Handle document deletion
if 'delete_transcript' in st.session_state and st.session_state.delete_transcript:
    delete_transcript(st.session_state.delete_transcript)
    # Also delete associated rewrites and ideas
    delete_rewrite(st.session_state.delete_transcript)
    delete_post_ideas(st.session_state.delete_transcript)
    st.session_state.delete_transcript = None
    st.rerun()

# Update the section that initializes the transcript state

transcripts = get_all_transcripts()
if transcripts:
    for i, transcript in enumerate(transcripts):
        delete_key = f"delete_{transcript.id}"
        ideas_key = f"ideas_{transcript.id}"
        rewrite_key = f"rewrite_{transcript.id}"
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
            
            # Initialize rewrite state for this transcript if needed
            if transcript.id not in st.session_state.show_rewrite_tab:
                # Check if rewrites exist for this transcript in the database
                existing_rewrite = get_rewrite(transcript.id)
                
                # If rewrite exists in DB, show the tab automatically
                st.session_state.show_rewrite_tab[transcript.id] = existing_rewrite is not None
                st.session_state.generating_rewrite[transcript.id] = False
                
                # Store the rewrite content in session state if available
                if existing_rewrite:
                    st.session_state.rewrite_content[transcript.id] = existing_rewrite["content"]
                    st.session_state.rewrite_options[transcript.id] = existing_rewrite["options"]
                else:
                    st.session_state.rewrite_options[transcript.id] = []
            
            # Get current state
            show_ideas = st.session_state.show_ideas_tab[transcript.id]
            show_rewrite = st.session_state.show_rewrite_tab[transcript.id]
            
            # Create tabs based on what should be shown
            if show_ideas and show_rewrite:
                processed_tab, original_tab, ideas_tab, rewrite_tab = st.tabs([
                    "Processed", "Original", "Post Ideas", "Rewrite"
                ])
            elif show_ideas:
                processed_tab, original_tab, ideas_tab = st.tabs([
                    "Processed", "Original", "Post Ideas"
                ])
            elif show_rewrite:
                processed_tab, original_tab, rewrite_tab = st.tabs([
                    "Processed", "Original", "Rewrite"
                ])
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
                
                # Add Rewrite button and options
                with st.container():
                    # Get or initialize rewrite options for this transcript
                    if transcript.id not in st.session_state.rewrite_options:
                        st.session_state.rewrite_options[transcript.id] = []
                    
                    # Modify the part where you're handling the multiselect options
                    # Get the existing database options and ensure they match the format in the multiselect
                    if transcript.id in st.session_state.rewrite_options and st.session_state.rewrite_options[transcript.id]:
                        # Normalize the saved options to match exactly what's in the multiselect dropdown
                        normalized_options = []
                        for option in st.session_state.rewrite_options[transcript.id]:
                            if isinstance(option, str):
                                # Convert options like "youtube_script" to "YouTube Script"
                                if option.lower() == "clear_simple":
                                    normalized_options.append("Clear & Simple")
                                elif option.lower() == "professional":
                                    normalized_options.append("Professional")
                                elif option.lower() == "storytelling":
                                    normalized_options.append("Storytelling")
                                elif option.lower() == "youtube_script":
                                    normalized_options.append("YouTube Script")
                                elif option.lower() == "educational":
                                    normalized_options.append("Educational")
                                elif option.lower() == "balanced":
                                    normalized_options.append("Balanced")
                                elif option.lower() == "shorter":
                                    normalized_options.append("Shorter")
                                elif option.lower() == "longer":
                                    normalized_options.append("Longer")
                                # Add direct matches
                                elif option in ["Clear & Simple", "Professional", "Storytelling", "YouTube Script", "Educational", "Balanced", "Shorter", "Longer"]:
                                    normalized_options.append(option)

                        # Update the session state with normalized options
                        st.session_state.rewrite_options[transcript.id] = normalized_options

                    # Now use the normalized options in the multiselect
                    available_options = [
                        "Clear & Simple", # Replaces Authoritative - confident but 8th grade level
                        "Professional", # New - business appropriate, measured tone
                        "Storytelling", # New - narrative structure with engaging flow
                        "YouTube Script",
                        "Educational", # New - explains concepts clearly with examples
                        "Balanced", # New - replaces Conversational - mature but approachable
                        "Shorter",
                        "Longer"
                    ]

                    # Filter default values to ensure they exist in options
                    default_options = []
                    for opt in st.session_state.rewrite_options.get(transcript.id, []):
                        if opt in available_options:
                            default_options.append(opt)

                    # Use the filtered defaults
                    options = st.multiselect(
                        "Rewrite Options",
                        available_options,
                        default=default_options,
                        key=f"options_{transcript.id}"
                    )
                    
                    # Check for contradictory options
                    if "Shorter" in options and "Longer" in options:
                        st.error("Cannot select both 'Shorter' and 'Longer' options. Please choose only one.")
                        if "Shorter" in options and "Shorter" not in st.session_state.rewrite_options.get(transcript.id, []):
                            options.remove("Longer")
                        elif "Longer" in options and "Longer" not in st.session_state.rewrite_options.get(transcript.id, []):
                            options.remove("Shorter")
                    
                    # Update options in session state
                    st.session_state.rewrite_options[transcript.id] = options
                    
                    # Define the rewrite button here - THIS WAS MISSING
                    rewrite_button = st.button("Rewrite", key=rewrite_key, 
                                              disabled=len(options) == 0)
                    
                    # Handle rewrite button click
                    if rewrite_button:
                        if len(options) > 0:
                            st.session_state.show_rewrite_tab[transcript.id] = True
                            st.session_state.generating_rewrite[transcript.id] = True
                            st.rerun()
                        else:
                            st.error("Please select at least one rewrite option.")
            
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
                        
                        # Add action buttons without the container
                        col1, col2, col3, col4 = st.columns(4)
                        
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
                        
                        with col4:
                            # Add download button
                            st.download_button(
                                "Download Ideas",
                                st.session_state.post_ideas[transcript.id],
                                file_name=f"{transcript.filename.split('.')[0]}_post_ideas.md",
                                mime="text/markdown",
                                key=f"download_ideas_{transcript.id}"
                            )
            
            # Handle Rewrite tab if activated
            if show_rewrite:
                with rewrite_tab:
                    # Check if we need to generate a rewrite
                    if st.session_state.generating_rewrite[transcript.id]:
                        with st.spinner("Rewriting transcript... This may take a moment."):
                            # Process options to lowercase for API
                            api_options = [opt.lower().replace(" ", "_") for opt in st.session_state.rewrite_options[transcript.id]]
                            
                            # Either load existing rewrite or generate new one
                            existing_rewrite = get_rewrite(transcript.id)
                            
                            # Check if rewrite exists with same options
                            if existing_rewrite and set(existing_rewrite["options"]) == set(api_options):
                                rewrite_content = existing_rewrite["content"]
                            else:
                                # Generate new rewrite
                                rewrite_content = rewrite_transcript(clean_content, api_options)
                            
                            st.session_state.rewrite_content[transcript.id] = rewrite_content
                            st.session_state.generating_rewrite[transcript.id] = False
                    
                    # Display rewrite content
                    if transcript.id in st.session_state.rewrite_content:
                        content = st.session_state.rewrite_content[transcript.id]
                        
                        # Check for error message
                        if content.startswith("ERROR:"):
                            st.error(content)
                        else:
                            if "#" in content or "**" in content or "*" in content:
                                st.markdown(content)
                            else:
                                st.text_area("Rewritten Content", content, height=300)
                            
                            # Add action buttons without the container
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                if st.button("Regenerate", key=f"regenerate_rewrite_{transcript.id}"):
                                    st.session_state.generating_rewrite[transcript.id] = True
                                    st.rerun()
                                    
                            with col2:
                                if st.button("Save Rewrite", key=f"save_rewrite_{transcript.id}"):
                                    selected_options = options
                                    save_rewrite(transcript.id, content, selected_options)
                                    st.success("Rewrite saved successfully!")
                                    
                            with col3:
                                if st.button("Delete Rewrite", key=f"delete_rewrite_{transcript.id}"):
                                    success = delete_rewrite(transcript.id)
                                    if success:
                                        st.success("Rewrite deleted successfully")
                                        st.session_state.rewrite_content.pop(transcript.id, None)
                                        st.session_state.show_rewrite_tab[transcript.id] = False
                                        st.session_state.rewrite_options[transcript.id] = []
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete rewrite from database")
                                
                            with col4:
                                st.download_button(
                                    "Download Rewrite",
                                    content,
                                    file_name=f"{transcript.filename.split('.')[0]}_rewritten.md",
                                    mime="text/markdown",
                                    key=f"download_rewrite_{transcript.id}"
                                )
else:
    st.info("No transcripts have been processed yet.")



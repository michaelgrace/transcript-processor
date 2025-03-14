import streamlit as st
import os
from processor import detect_and_process
from database import save_transcript, get_transcript, get_all_transcripts
import markdown

st.set_page_config(page_title="Transcript Processor", layout="wide")

st.title("Transcript Processor")
st.write("Upload an SRT file or text transcript to convert it into a readable format.")

# Add before the "formatting options"
st.info(f"Using AI model: {os.getenv('AI_MODEL', 'Not specified')} | API Key configured: {'Yes' if os.getenv('API_KEY') else 'No'}")

# Formatting options section
with st.expander("Formatting Options", expanded=True):
    st.write("Select the formatting elements to apply:")
    col1, col2 = st.columns(2)
    
    with col1:
        add_paragraphs = st.checkbox("Paragraph Structure", value=True)
        add_headings = st.checkbox("Add Headings for Topics", value=True)
    
    with col2:
        fix_grammar = st.checkbox("Fix Grammar & Punctuation", value=True)
        highlight_key_points = st.checkbox("Highlight Key Points", value=True)
    
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
    
    # Create tabs for original and processed content
    tab1, tab2 = st.tabs(["Original Content", "Processed Content"])
    
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

# Display past transcripts
transcripts = get_all_transcripts()
if transcripts:
    for transcript in transcripts:
        with st.expander(f"{transcript.filename} (ID: {transcript.id})"):
            tab1, tab2 = st.tabs(["Original", "Processed"])
            with tab1:
                st.text_area("Original Content", transcript.original_content, height=200)
            with tab2:
                # Check if content appears to be Markdown
                if "#" in transcript.processed_content or "**" in transcript.processed_content or "*" in transcript.processed_content:
                    st.markdown(transcript.processed_content)
                else:
                    st.text_area("Processed Content", transcript.processed_content, height=200)
else:
    st.info("No transcripts have been processed yet.")
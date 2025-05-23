import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta
import sys
import requests

# Ensure the app directory is in sys.path for module resolution in all environments
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure page after imports
st.set_page_config(
    page_title="Transcript Processor",
    page_icon="📝",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://api:8000")  # Or your API endpoint

# Add this before you use st.session_state.user_role anywhere in your code
# Preferably close to the top, after st.set_page_config
if 'user_role' not in st.session_state:
    st.session_state.user_role = "admin"  # Default to admin for now

# Initialize session state for expandable/history features if not present
if 'show_ideas_tab' not in st.session_state:
    st.session_state.show_ideas_tab = {}
if 'generating_ideas' not in st.session_state:
    st.session_state.generating_ideas = {}
if 'post_ideas' not in st.session_state:
    st.session_state.post_ideas = {}

# Configure the page with minimal padding
# Enhanced CSS with stronger hiding rules for branding and subtle button styling
st.markdown("""
<style>
/* Core layout settings */
.appview-container .main .block-container {
    padding-top: .5rem !important;
    padding-bottom: .5rem !important;
    max-width: 100% !important;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {visibility: hidden !important;}
.decoration {display: none !important;}

/* Button styling */
.stButton > button, .stDownloadButton > button {
    width: auto !important;
}

.stButton, .stDownloadButton {
    display: inline-block !important;
    width: auto !important;
    margin-right: 1em;
}

/* Component sizing */
div[data-testid="stMultiSelect"] {
    min-width: 200px !important;
    max-width: 400px !important;
    display: inline-block !important;
}

/* Layout containers */
.block-container {
    max-width: 100% !important;
    padding: 0.5rem 1rem !important;
}

/* Print settings */
@media print {
    .streamlit-container { padding: 0 !important; }
    header, footer, .stButton, .stDownloadButton { display: none !important; }
    .main { padding: 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

st.title("Transcript Processor")
st.write("Upload an SRT file or text transcript to convert it into a readable format.")

# Set up defaults from session state, or use hardcoded defaults if not present
add_paragraphs = st.session_state.get("add_paragraphs", True)
add_headings = st.session_state.get("add_headings", False)
fix_grammar = st.session_state.get("fix_grammar", True)
highlight_key_points = st.session_state.get("highlight_key_points", True)
format_style = st.session_state.get("format_style", "Article")
rewrite_options = st.session_state.get("rewrite_options", [])
uniqueness_level = st.session_state.get("uniqueness_level", 0.7)

# Formatting options section
with st.expander("Formatting Options", expanded=False):
    st.write("Select the formatting elements to apply:")
    col1, col2 = st.columns(2)
    
    with col1:
        add_paragraphs = st.checkbox(
            "Paragraph Structure", 
            value=add_paragraphs,
            help="Organize content into logical paragraphs based on topics"
        )
        add_headings = st.checkbox(
            "Add Headings for Topics", 
            value=add_headings,
            help="Insert section headings to highlight main topics"
        )
    
    with col2:
        fix_grammar = st.checkbox(
            "Fix Grammar & Punctuation", 
            value=fix_grammar,
            help="Correct grammar and punctuation while preserving meaning"
        )
        highlight_key_points = st.checkbox(
            "Highlight Key Points", 
            value=highlight_key_points,
            help="Bold important concepts and conclusions"
        )
    
    format_style = st.radio(
        "Document Style",
        ["Article", "Transcript", "Meeting Notes", "Academic"],
        horizontal=True,
        index=["Article", "Transcript", "Meeting Notes", "Academic"].index(format_style)
    )

    # Rewrite options as multiselect (already implemented)
    rewrite_options = st.multiselect(
        "Rewrite Style Options",
        [
            "Clear & Simple",
            "Professional",
            "Storytelling",
            "YouTube Script",
            "Educational",
            "Balanced",
            "Shorter",
            "Longer"
        ],
        default=rewrite_options,
        help="Choose one or more rewrite styles to apply to the processed content."
    )

    uniqueness_level = st.number_input(
        "Uniqueness Level (AI Creativity)",
        min_value=0.0,
        max_value=1.0,
        value=uniqueness_level,
        step=0.05,
        help="Increase for more creative and unique rewriting. Lower for more literal/faithful output."
    )

if st.session_state.user_role == "admin":
    with st.expander("📊 Analytics Dashboard", expanded=False):

        # Add before the "analytic charts"
        st.info(f"Using AI model: {os.getenv('AI_MODEL', 'Not specified')} | API Key configured: {'Yes' if os.getenv('API_KEY') else 'No'}")

        response = requests.get(f"{API_URL}/analytics/")
        if response.ok:
            analytics = response.json()
        else:
            analytics = {}

        # Create a 2-column layout for charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<h3>Popular Rewrite Options</h3>", unsafe_allow_html=True)
            if "popular_options" in analytics and analytics["popular_options"]:
                df_options = pd.DataFrame(analytics["popular_options"], columns=["Options", "Count"])
                df_options["Options"] = df_options["Options"].map(lambda x: x.replace("_", " ").title())
                fig = px.pie(df_options, values="Count", names="Options")
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=200,
                    legend=dict(font=dict(size=8)),
                    font=dict(size=9),
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No rewrite options data available yet")
            
            st.markdown("<h3>Format Styles</h3>", unsafe_allow_html=True)
            if "popular_formats" in analytics and analytics["popular_formats"]:
                df_formats = pd.DataFrame(analytics["popular_formats"], columns=["Format", "Count"])
                fig = px.bar(df_formats, x="Format", y="Count")
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=200,
                    font=dict(size=9),
                    xaxis_title="",
                    yaxis_title=""
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No format style data available yet")
        
        with col2:
            st.markdown("<h3>Common Topics</h3>", unsafe_allow_html=True)
            if "common_topics" in analytics and analytics["common_topics"]:
                df_topics = pd.DataFrame(analytics["common_topics"], columns=["Topic", "Count"])
                fig = px.bar(df_topics, x="Topic", y="Count")
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=200,
                    font=dict(size=9),
                    xaxis_title="",
                    yaxis_title=""
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No topic data available yet")
            
            st.markdown("<h3>Sentiment Distribution</h3>", unsafe_allow_html=True)
            if "sentiment_distribution" in analytics and analytics["sentiment_distribution"]:
                df_sentiment = pd.DataFrame(analytics["sentiment_distribution"], 
                                         columns=["Sentiment", "Count"])
                colors = {
                    'positive': 'green',
                    'negative': 'red',
                    'neutral': 'blue'
                }
                fig = px.pie(df_sentiment, values="Count", names="Sentiment", 
                           color="Sentiment", color_discrete_map=colors)
                fig.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    height=200,
                    legend=dict(font=dict(size=8)),
                    font=dict(size=9),
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info("No sentiment data available yet")

# Add two tabs: Upload File (default) and Paste Text
tab_upload, tab_paste = st.tabs(["Upload File", "Paste Text"])

with tab_upload:
    # Update the file uploader to accept PDF files
    uploaded_file = st.file_uploader("Choose a file", type=["srt", "txt", "pdf"])

    if uploaded_file is not None:
        # Read file content
        try:
            files = {"file": uploaded_file}
            data = {
                "add_paragraphs": str(add_paragraphs).lower(),
                "add_headings": str(add_headings).lower(),
                "fix_grammar": str(fix_grammar).lower(),
                "highlight_key_points": str(highlight_key_points).lower(),
                "format_style": format_style,
                "rewrite_options": rewrite_options,
                "uniqueness_level": uniqueness_level
            }
            response = requests.post(f"{API_URL}/upload/", files=files, data=data)
            if response.ok:
                result = response.json()
                processed_content = result["processed_content"]
                file_content = result["original_content"]
                transcript_id = result["transcript_id"]
                metadata = result.get("metadata", {})
                st.success("Processing complete!")
            else:
                st.error("API error: could not process file")

            # Save the user's selections to session state
            st.session_state["add_paragraphs"] = add_paragraphs
            st.session_state["add_headings"] = add_headings
            st.session_state["fix_grammar"] = fix_grammar
            st.session_state["highlight_key_points"] = highlight_key_points
            st.session_state["format_style"] = format_style
            st.session_state["rewrite_options"] = rewrite_options
            st.session_state["uniqueness_level"] = uniqueness_level

            # Create tabs for original and processed content
            tab2, tab1 = st.tabs(["Processed Content", "Original Content"])
            
            with tab1:
                st.text_area("Original Content", file_content, height=300, key="upload_original_content")
            
            with tab2:
                # Editable processed content
                edited_processed_content = st.text_area(
                    "Processed Content (editable)", 
                    value=processed_content, 
                    height=300, 
                    key="upload_processed_content_edit"
                )
                
                # Download button
                st.download_button(
                    "Download Markdown",
                    edited_processed_content,
                    file_name=f"{os.path.splitext(uploaded_file.name)[0]}_formatted.md",
                    mime="text/markdown"
                )
                    
                # Save button
                if st.button("Save to Database"):
                    response = requests.patch(
                        f"{API_URL}/transcript/{transcript_id}",
                        json={"processed_content": edited_processed_content}
                    )
                    if response.ok:
                        st.success("Processed content updated!")
                    else:
                        st.error("Failed to update transcript.")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

with tab_paste:
    st.subheader("Paste or Edit Transcript Text")
    pasted_text = st.text_area("Paste your transcript here", height=300, key="pasted_text_area")
    pasted_title = st.text_input("Title", key="pasted_title")

    if st.button("Process Pasted Text", key="process_pasted_text"):
        if not pasted_text.strip():
            st.warning("Please paste some text to process.")
        elif not pasted_title.strip():
            st.warning("Please specify a title.")
        else:
            with st.spinner("Processing pasted text..."):
                data = {
                    "text": pasted_text,
                    "title": pasted_title,
                    "add_paragraphs": str(add_paragraphs).lower(),
                    "add_headings": str(add_headings).lower(),
                    "fix_grammar": str(fix_grammar).lower(),
                    "highlight_key_points": str(highlight_key_points).lower(),
                    "format_style": format_style,
                    "rewrite_options": rewrite_options,
                    "uniqueness_level": uniqueness_level
                }
                response = requests.post(f"{API_URL}/process_text/", json=data)
                if response.ok:
                    result = response.json()
                    processed_content = result["processed_content"]
                    transcript_id = result["transcript_id"]
                    st.session_state["pasted_processed_content"] = processed_content
                    st.session_state["pasted_original_content"] = pasted_text
                    st.success("Processing complete!")
                else:
                    st.error("API error: could not process text.")

                # Save the user's selections to session state
                st.session_state["add_paragraphs"] = add_paragraphs
                st.session_state["add_headings"] = add_headings
                st.session_state["fix_grammar"] = fix_grammar
                st.session_state["highlight_key_points"] = highlight_key_points
                st.session_state["format_style"] = format_style
                st.session_state["rewrite_options"] = rewrite_options
                st.session_state["uniqueness_level"] = uniqueness_level

    # Show processed content if available
    if st.session_state.get("pasted_processed_content"):
        tab2, tab1 = st.tabs(["Processed Content", "Original Content"])
        with tab1:
            st.text_area("Original Content", st.session_state.get("pasted_original_content", ""), height=300, key="pasted_original_content_display")
        with tab2:
            # Editable processed content
            edited_paste_content = st.text_area(
                "Processed Content (editable)",
                value=st.session_state["pasted_processed_content"],
                height=300,
                key="pasted_processed_content_edit"
            )
            download_title = pasted_title.strip() or "pasted_content"
            st.download_button(
                "Download Text",
                edited_paste_content,
                file_name=f"{download_title}.txt",
                mime="text/plain"
            )
            # Save to DB button
            if st.button("Save to Database", key="save_pasted_to_db"):
                response = requests.patch(
                    f"{API_URL}/transcript/{transcript_id}",
                    json={"processed_content": edited_paste_content}
                )
                if response.ok:
                    st.success("Processed content updated!")
                else:
                    st.error("Failed to update transcript.")

# History section
st.divider()
st.subheader("Previously Processed Transcripts")

response = requests.get(f"{API_URL}/transcripts/")
if response.ok:
    transcripts = response.json()
else:
    transcripts = []

if transcripts:
    for i, transcript in enumerate(transcripts):
        delete_key = f"delete_{transcript['id']}"
        ideas_key = f"ideas_{transcript['id']}"
        expander_label = f"**{transcript['filename']}** (ID: {transcript['id']})"
        
        with st.expander(expander_label):
            # Initialize state for this transcript if needed
            if transcript['id'] not in st.session_state.show_ideas_tab:
                # Check if post ideas exist for this transcript in the database
                response = requests.get(f"{API_URL}/post_ideas/{transcript['id']}")
                if response.ok:
                    existing_ideas = response.json()
                    # Fix: If API returns an object with 'post_ideas' key, extract it
                    if isinstance(existing_ideas, dict) and "post_ideas" in existing_ideas:
                        existing_ideas = existing_ideas["post_ideas"]
                else:
                    existing_ideas = None

                st.session_state.show_ideas_tab[transcript['id']] = bool(existing_ideas)
                st.session_state.generating_ideas[transcript['id']] = False

                if existing_ideas:
                    st.session_state.post_ideas[transcript['id']] = existing_ideas
                else:
                    st.session_state.post_ideas[transcript['id']] = ""
            
            # Get current state
            show_ideas = st.session_state.show_ideas_tab[transcript['id']]
            
            # Create tabs based on what should be shown
            tabs = []
            tab_names = ["Processed", "Original"]

            if show_ideas:
                tab_names.append("Post Ideas")
            if st.session_state.user_role == "admin":  # Only show these tabs for admin users
                tab_names.append("Metadata")

            all_tabs = st.tabs(tab_names)

            # Map tab variables to actual tabs
            processed_tab = all_tabs[0]
            original_tab = all_tabs[1]
            current_tab_index = 2

            # Conditionally assign the rest of the tabs
            if show_ideas:
                ideas_tab = all_tabs[current_tab_index]
                current_tab_index += 1

            if st.session_state.user_role == "admin":
                metadata_tab = all_tabs[current_tab_index]
                current_tab_index += 1
            
            with original_tab:
                st.text_area("Original Content", transcript['original_content'], height=200, key=f"original_content_{transcript['id']}")
            
            with processed_tab:
                # Don't include the transcript filename header here since it's already in the expander
                st.markdown(transcript['processed_content'], unsafe_allow_html=True)
                
                # Fix download button to use processed_content instead of transcript.processed_content
                st.download_button(
                    "Download Transcript",
                    transcript['processed_content'],  # Changed from transcript.processed_content
                    file_name=f"{transcript['filename'].split('.')[0]}_processed.md",
                    mime="text/markdown",
                    key=f"download_{transcript['id']}"
                )
                
                # Add delete button below download with same styling
                if st.button("Delete Transcript", key=delete_key):
                    response = requests.delete(f"{API_URL}/transcript/{transcript['id']}")
                    if response.ok:
                        st.success("Transcript deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete transcript.")
                
                # Add Post Ideas button
                if st.button("Post Ideas", key=ideas_key):
                    # Toggle the state
                    st.session_state.show_ideas_tab[transcript['id']] = True
                    st.session_state.generating_ideas[transcript['id']] = True
                    st.rerun()
            
            # Handle Ideas tab if activated
            if show_ideas:
                with ideas_tab:
                    # Check if we need to generate ideas or load from database
                    if st.session_state.generating_ideas[transcript['id']]:
                        with st.spinner("Generating post ideas..."):
                            response = requests.post(
                                f"{API_URL}/generate_post_ideas/",
                                json={"processed_content": transcript['processed_content']}
                            )
                            if response.ok:
                                ideas_content = response.json()["post_ideas"]
                                st.session_state.post_ideas[transcript['id']] = ideas_content
                            else:
                                st.error("Failed to generate post ideas.")
                            
                            # Reset the generating flag
                            st.session_state.generating_ideas[transcript['id']] = False
                    
                    # Display ideas content
                    if transcript['id'] in st.session_state.post_ideas:
                        content = st.session_state.post_ideas[transcript['id']]
                        
                        # Display content in a text area to allow editing
                        edited_content = st.text_area(
                            "Generated Post Ideas",
                            value=content,
                            height=300,
                            key=f"post_ideas_text_{transcript['id']}"
                        )
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("Save Ideas", key=f"save_ideas_{transcript['id']}"):
                                response = requests.patch(
                                    f"{API_URL}/post_ideas/{transcript['id']}",
                                    json={"post_ideas": edited_content}
                                )
                                if response.ok:
                                    st.success("Post ideas saved successfully!")
                                    st.session_state.post_ideas[transcript['id']] = edited_content
                                else:
                                    st.error("Failed to save post ideas.")
                        
                        with col2:
                            # Delete button
                            if st.button("Delete Ideas", key=f"delete_ideas_{transcript['id']}"):
                                response = requests.delete(f"{API_URL}/post_ideas/{transcript['id']}")
                                if response.ok:
                                    st.success("Ideas deleted successfully")
                                    st.session_state.post_ideas.pop(transcript['id'], None)
                                    st.session_state.show_ideas_tab[transcript['id']] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to delete ideas from database.")
                        
                        with col3:
                            # Add download button
                            st.download_button(
                                "Download Ideas",
                                st.session_state.post_ideas[transcript['id']],
                                file_name=f"{transcript['filename'].split('.')[0]}_post_ideas.md",
                                mime="text/markdown",
                                key=f"download_ideas_{transcript['id']}"
                            )

            if st.session_state.user_role == "admin" and "metadata_tab" in locals():
                with metadata_tab:
                    response = requests.get(f"{API_URL}/metadata/{transcript['id']}")
                    if response.ok:
                        metadata = response.json()
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Topics")
                            topics = metadata.get("topics", [])
                            if topics:
                                for topic in topics:
                                    st.write(f"• {topic}")
                            else:
                                st.write("No topics detected")
                                
                            st.subheader("Keywords")
                            keywords = metadata.get("keywords", [])
                            if keywords:
                                st.write(", ".join(keywords))
                            else:
                                st.write("No keywords detected")
                        
                        with col2:
                            st.subheader("Tags")
                            tags = metadata.get("tags", [])
                            if tags:
                                for tag in tags:
                                    st.write(f"• {tag}")
                            else:
                                st.write("No tags detected")
                                
                            st.subheader("Sentiment")
                            sentiment = metadata.get("sentiment", {})
                            if sentiment:
                                sentiment_type = sentiment.get("classification", "neutral")
                                confidence = sentiment.get("confidence", 0.5)
                                
                                if sentiment_type == "positive":
                                    st.success(f"Positive (Confidence: {confidence:.2f})")
                                elif sentiment_type == "negative":
                                    st.error(f"Negative (Confidence: {confidence:.2f})")
                                else:
                                    st.info(f"Neutral (Confidence: {confidence:.2f})")
                                    
                        # Button to refresh metadata analysis
                        if st.button("Refresh Metadata Analysis", key=f"refresh_metadata_{transcript['id']}"):
                            with st.spinner("Analyzing content..."):
                                response = requests.post(
                                    f"{API_URL}/analyze_metadata/",
                                    json={"processed_content": transcript['processed_content']}
                                )
                                if response.ok:
                                    metadata = response.json()
                                    st.success("Metadata updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to update metadata.")
                    else:
                        st.info("No metadata available for this transcript.")
                        if st.button("Generate Metadata", key=f"generate_metadata_{transcript['id']}"):
                            with st.spinner("Analyzing content..."):
                                response = requests.post(
                                    f"{API_URL}/analyze_metadata/",
                                    json={"processed_content": transcript['processed_content']}
                                )
                                if response.ok:
                                    metadata = response.json()
                                    st.success("Metadata generated successfully!")
                                    st.rerun()
                                else:
                                    st.error("Failed to generate metadata.")

else:
    st.info("No transcripts have been processed yet.")



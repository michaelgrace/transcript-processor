import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta

# Configure page after imports
st.set_page_config(
    page_title="Transcript Processor",
    page_icon="📝",
    layout="wide"
)

from processor import detect_and_process, generate_post_ideas, rewrite_transcript, analyze_transcript_metadata
from database import (
    save_transcript, get_transcript, get_all_transcripts, delete_transcript, 
    save_post_ideas, get_post_ideas, delete_post_ideas,
    save_rewrite, get_rewrite, delete_rewrite,
    save_transcript_metadata, get_transcript_metadata, 
    log_analytics_event, get_analytics_summary
)

# In main.py, after imports
from database import ensure_tables_exist
import threading

# Run database initialization in background thread so it doesn't block the UI
threading.Thread(target=ensure_tables_exist, daemon=True).start()

# Add this before you use st.session_state.user_role anywhere in your code
# Preferably close to the top, after st.set_page_config
if 'user_role' not in st.session_state:
    st.session_state.user_role = "admin"  # Default to admin for now

# Configure the page with minimal padding
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

/* Make sidebar narrower */
[data-testid="stSidebar"] {
    width: 250px !important;
    min-width: 250px !important;
}

/* Adjust text in sidebar to prevent wrapping when possible */
[data-testid="stSidebar"] .stMarkdown {
    font-size: 0.9em;
}

/* Adjust expander width in sidebar */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    width: 100% !important;
}

/* Make plots in sidebar fit */
[data-testid="stSidebar"] .stPlotlyChart {
    width: 100% !important;
}

/* Reduce font size in analytics dashboard */
[data-testid="stSidebar"] h3 {
    font-size: 1.1rem !important;
    margin-top: 0.8rem !important;
    margin-bottom: 0.5rem !important;
}

/* Reduce top margin for page title */
.appview-container .main .block-container {
    padding-top: .5rem !important;
    padding-bottom: .5rem !important;
    max-width: 100% !important;  /* Make the main container full width */
}

/* Make the content area use more width */
.css-1d391kg, .css-1lcbmhc, .css-12oz5g7 {
    max-width: 100% !important;
}

/* Make all Streamlit containers full width */
.block-container {
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* Hide streamlit branding with !important */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
</style>
""", unsafe_allow_html=True)

st.title("Transcript Processor")
st.write("Upload an SRT file or text transcript to convert it into a readable format.")

# Formatting options section
with st.expander("Formatting Options", expanded=False):
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

if st.session_state.user_role == "admin":
    with st.expander("📊 Analytics Dashboard", expanded=False):

        # Add before the "analytic charts"
        st.info(f"Using AI model: {os.getenv('AI_MODEL', 'Not specified')} | API Key configured: {'Yes' if os.getenv('API_KEY') else 'No'}")

        analytics = get_analytics_summary()
        
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

# Update the file uploader to accept PDF files
uploaded_file = st.file_uploader("Choose a file", type=["srt", "txt", "pdf"])

# Add this near your file upload code in main.py
if uploaded_file is not None:
    # Read file content
    try:
        if uploaded_file.name.lower().endswith('.pdf'):
            # Read file content as binary for PDFs
            file_content_binary = uploaded_file.read()
            
            # Log for debugging
            st.info(f"Processing PDF file: {uploaded_file.name}")
            
            # Process the binary content directly
            processed_content = detect_and_process(
                file_content_binary,
                uploaded_file.name,
                add_paragraphs,
                add_headings,
                fix_grammar,
                highlight_key_points,
                format_style,
                is_binary=True
            )
            
            # Also extract text for display in the original content tab
            from processor import extract_text_from_pdf
            file_content = extract_text_from_pdf(file_content_binary)
        else:
            # For non-PDF files, read as text
            file_content = uploaded_file.read().decode("utf-8")
            
            # Log for debugging
            st.info(f"Processing {uploaded_file.name.split('.')[-1].upper()} file: {uploaded_file.name}")
            
            # Process the file with formatting options
            with st.spinner("Processing transcript... This may take a moment."):
                processed_content = detect_and_process(
                    file_content, 
                    uploaded_file.name,
                    add_paragraphs,
                    add_headings,
                    fix_grammar,
                    highlight_key_points,
                    format_style
                )
                
                # Log success
                if processed_content:
                    st.success("Processing complete!")
                    print(f"Processed content length: {len(processed_content)}")
                else:
                    st.error("Processing failed - no content returned")

        # Create tabs for original and processed content
        tab2, tab1 = st.tabs(["Processed Content", "Original Content"])
        
        with tab1:
            st.text_area("Original Content", file_content, height=300, key="upload_original_content")
        
        with tab2:
            # Display processed content - no need to process again!
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
                st.text_area("Processed Content", processed_content, height=300, key="upload_processed_content")
                
            # Save button
            if st.button("Save to Database"):
                # Determine source type based on file extension
                source_type = "pdf" if uploaded_file.name.lower().endswith('.pdf') else "transcript"
                
                # Save transcript to database
                transcript_id = save_transcript(
                    filename=uploaded_file.name,
                    original_content=file_content,
                    processed_content=processed_content,
                    format_style=format_style,
                    source_type=source_type
                )
                
                # Only proceed if save was successful
                if transcript_id is not None:
                    # Generate and store metadata
                    with st.spinner("Analyzing content metadata..."):
                        metadata = analyze_transcript_metadata(processed_content)
                        if metadata:
                            success = save_transcript_metadata(transcript_id, metadata)
                            if not success:
                                st.warning("Metadata analysis saved with errors")
                    
                    # Log analytics event
                    log_analytics_event(
                        transcript_id, 
                        "format", 
                        {
                            "format_style": format_style,
                            "add_paragraphs": add_paragraphs,
                            "add_headings": add_headings,
                            "fix_grammar": fix_grammar,
                            "highlight_key_points": highlight_key_points
                        }
                    )
                    
                    st.success(f"Saved transcript with ID: {transcript_id}")
                else:
                    st.error("Failed to save transcript to database. Check logs for details.")
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# Add this just before the "History section" (where you have st.divider())

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

# Add this near your other session state initialization
if 'user_role' not in st.session_state:
    st.session_state.user_role = "admin"  # Default to admin for now, you can implement proper auth later

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
        #delete_key = f"delete_{transcript.id}"
        delete_key = f"delete_{transcript['id']}"
        ideas_key = f"ideas_{transcript['id']}"
        rewrite_key = f"rewrite_{transcript['id']}"
        expander_label = f"**{transcript['filename']}** (ID: {transcript['id']})"
        
        with st.expander(expander_label):
            # Initialize state for this transcript if needed
            if transcript['id'] not in st.session_state.show_ideas_tab:
                # Check if post ideas exist for this transcript in the database
                existing_ideas = get_post_ideas(transcript['id'])
                
                # If ideas exist in DB, show the tab automatically
                st.session_state.show_ideas_tab[transcript['id']] = existing_ideas is not None
                st.session_state.generating_ideas[transcript['id']] = False
                
                # Store the ideas content in session state if available
                if existing_ideas:
                    st.session_state.post_ideas[transcript['id']] = existing_ideas["content"]
            
            # Initialize rewrite state for this transcript if needed
            if transcript['id'] not in st.session_state.show_rewrite_tab:
                # Check if rewrites exist for this transcript in the database
                existing_rewrite = get_rewrite(transcript['id'])
                
                # If rewrite exists in DB, show the tab automatically
                st.session_state.show_rewrite_tab[transcript['id']] = existing_rewrite is not None
                st.session_state.generating_rewrite[transcript['id']] = False
                
                # Store the rewrite content in session state if available
                if existing_rewrite:
                    st.session_state.rewrite_content[transcript['id']] = existing_rewrite["content"]
                    st.session_state.rewrite_options[transcript['id']] = existing_rewrite["options"]
                else:
                    st.session_state.rewrite_options[transcript['id']] = []
            
            # Get current state
            show_ideas = st.session_state.show_ideas_tab[transcript['id']]
            show_rewrite = st.session_state.show_rewrite_tab[transcript['id']]
            
            # Create tabs based on what should be shown
            tabs = []
            tab_names = ["Processed", "Original"]

            if show_ideas:
                tab_names.append("Post Ideas")
            if show_rewrite:
                tab_names.append("Rewrite")
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

            if show_rewrite:
                rewrite_tab = all_tabs[current_tab_index]
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
                    st.session_state.delete_transcript = transcript['id']
                    st.rerun()
                
                # Add Post Ideas button
                if st.button("Post Ideas", key=ideas_key):
                    # Toggle the state
                    st.session_state.show_ideas_tab[transcript['id']] = True
                    st.session_state.generating_ideas[transcript['id']] = True
                    st.rerun()
                
                # Add Rewrite button and options
                with st.container():
                    # Get or initialize rewrite options for this transcript
                    if transcript['id'] not in st.session_state.rewrite_options:
                        st.session_state.rewrite_options[transcript['id']] = []
                    
                    # Modify the part where you're handling the multiselect options
                    # Get the existing database options and ensure they match the format in the multiselect
                    if transcript['id'] in st.session_state.rewrite_options and st.session_state.rewrite_options[transcript['id']]:
                        # Normalize the saved options to match exactly what's in the multiselect dropdown
                        normalized_options = []
                        for option in st.session_state.rewrite_options[transcript['id']]:
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

                        st.session_state.rewrite_options[transcript['id']] = normalized_options

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
                    for opt in st.session_state.rewrite_options.get(transcript['id'], []):
                        if opt in available_options:
                            default_options.append(opt)

                    # Use the filtered defaults
                    options = st.multiselect(
                        "Rewrite Options",
                        available_options,
                        default=default_options,
                        key=f"options_{transcript['id']}"
                    )
                    
                    # Check for contradictory options
                    if "Shorter" in options and "Shorter" not in st.session_state.rewrite_options.get(transcript['id'], []):
                        options.remove("Longer")
                    elif "Longer" in options and "Longer" not in st.session_state.rewrite_options.get(transcript['id'], []):
                        options.remove("Shorter")
                    
                    # Update options in session state
                    st.session_state.rewrite_options[transcript['id']] = options
                    
                    # Define the rewrite button here - THIS WAS MISSING
                    rewrite_button = st.button("Rewrite", key=rewrite_key, 
                                              disabled=len(options) == 0)
                    
                    # Handle rewrite button click
                    if rewrite_button:
                        if len(options) > 0:
                            st.session_state.show_rewrite_tab[transcript['id']] = True
                            st.session_state.generating_rewrite[transcript['id']] = True
                            st.rerun()
                        else:
                            st.error("Please select at least one rewrite option.")
            
            # Handle Ideas tab if activated
            if show_ideas:
                with ideas_tab:
                    # Check if we need to generate ideas or load from database
                    if st.session_state.generating_ideas[transcript['id']]:
                        with st.spinner("Generating post ideas..."):
                            # Either load existing ideas or generate new ones
                            existing_ideas = get_post_ideas(transcript['id'])
                            
                            if existing_ideas:
                                ideas_content = existing_ideas["content"]
                                st.session_state.post_ideas[transcript['id']] = ideas_content
                            else:
                                # Generate new ideas
                                ideas_content = generate_post_ideas(transcript['processed_content'])
                                st.session_state.post_ideas[transcript['id']] = ideas_content
                                
                            # Reset the generating flag
                            st.session_state.generating_ideas[transcript['id']] = False
                    
                    # Display ideas content
                    if transcript['id'] in st.session_state.post_ideas:
                        st.text_area("Post Ideas", st.session_state.post_ideas[transcript['id']], height=300, key=f"ideas_content_{transcript['id']}")
                        
                        # Add action buttons without the container
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            # Regenerate button
                            if st.button("Regenerate Ideas", key=f"regenerate_{transcript['id']}"):
                                st.session_state.generating_ideas[transcript['id']] = True
                                st.rerun()
                                
                        with col2:
                            # Save button
                            if st.button("Save Ideas", key=f"save_ideas_{transcript['id']}"):
                                save_post_ideas(transcript['id'], st.session_state.post_ideas[transcript['id']])
                                
                                # Log analytics for post ideas
                                log_analytics_event(
                                    transcript['id'],
                                    "generate_ideas",
                                    {}
                                )
                                
                                st.success("Ideas saved successfully!")
                                
                        with col3:
                            # Delete button
                            if st.button("Delete Ideas", key=f"delete_ideas_{transcript['id']}"):
                                success = delete_post_ideas(transcript['id'])
                                if success:
                                    st.success("Ideas deleted successfully")
                                    st.session_state.post_ideas.pop(transcript['id'], None)
                                    st.session_state.show_ideas_tab[transcript['id']] = False
                                    st.rerun()
                                else:
                                    st.error("Failed to delete ideas from database")
                        
                        with col4:
                            # Add download button
                            st.download_button(
                                "Download Ideas",
                                st.session_state.post_ideas[transcript['id']],
                                file_name=f"{transcript['filename'].split('.')[0]}_post_ideas.md",
                                mime="text/markdown",
                                key=f"download_ideas_{transcript['id']}"
                            )
            
            # Handle Rewrite tab if activated
            if show_rewrite:
                with rewrite_tab:
                    # Check if we need to generate a rewrite
                    if st.session_state.generating_rewrite[transcript['id']]:
                        with st.spinner("Rewriting transcript... This may take a moment."):
                            # Process options to lowercase for API
                            api_options = [opt.lower().replace(" ", "_") for opt in st.session_state.rewrite_options[transcript['id']]]
                            
                            # Either load existing rewrite or generate new one
                            existing_rewrite = get_rewrite(transcript['id'])
                            
                            # Check if rewrite exists with same options
                            if existing_rewrite and set(existing_rewrite["options"]) == set(api_options):
                                rewrite_content = existing_rewrite["content"]
                            else:
                                # Generate new rewrite
                                rewrite_content = rewrite_transcript(transcript['processed_content'], api_options)
                            
                            st.session_state.rewrite_content[transcript['id']] = rewrite_content
                            st.session_state.generating_rewrite[transcript['id']] = False
                    
                    # Display rewrite content
                    if transcript['id'] in st.session_state.rewrite_content:
                        content = st.session_state.rewrite_content[transcript['id']]
                        
                        # Check for error message
                        if content.startswith("ERROR:"):
                            st.error(content)
                        else:
                            if "#" in content or "**" in content or "*" in content:
                                st.markdown(content)
                            else:
                                st.text_area("Rewritten Content", content, height=300, key=f"rewrite_content_{transcript['id']}")
                            
                            # Add action buttons without the container
                            col1, col2, col3, col4 = st.columns(4)

                            with col1:
                                if st.button("Regenerate", key=f"regenerate_rewrite_{transcript['id']}"):
                                    st.session_state.generating_rewrite[transcript['id']] = True
                                    st.rerun()
                                    
                            with col2:
                                if st.button("Save Rewrite", key=f"save_rewrite_{transcript['id']}"):
                                    selected_options = options
                                    save_rewrite(transcript['id'], content, selected_options)
                                    
                                    # Log analytics for this rewrite
                                    log_analytics_event(
                                        transcript['id'],
                                        "rewrite",
                                        {"options": selected_options}
                                    )
                                    
                                    st.success("Rewrite saved successfully!")
                                    
                            with col3:
                                if st.button("Delete Rewrite", key=f"delete_rewrite_{transcript['id']}"):
                                    success = delete_rewrite(transcript['id'])
                                    if success:
                                        st.success("Rewrite deleted successfully")
                                        st.session_state.rewrite_content.pop(transcript['id'], None)
                                        st.session_state.show_rewrite_tab[transcript['id']] = False
                                        st.session_state.rewrite_options[transcript['id']] = []
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete rewrite from database")
                                
                            with col4:
                                st.download_button(
                                    "Download Rewrite",
                                    content,
                                    file_name=f"{transcript['filename'].split('.')[0]}_rewritten.md",
                                    mime="text/markdown",
                                    key=f"download_rewrite_{transcript['id']}"
                                )

            if st.session_state.user_role == "admin" and "metadata_tab" in locals():
                with metadata_tab:
                    metadata = get_transcript_metadata(transcript['id'])
                    if metadata:
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
                                metadata = analyze_transcript_metadata(transcript['processed_content'])
                                if metadata:
                                    save_transcript_metadata(transcript['id'], metadata)
                                    st.success("Metadata updated successfully!")
                                    st.rerun()
                    else:
                        st.info("No metadata available for this transcript.")
                        if st.button("Generate Metadata", key=f"generate_metadata_{transcript['id']}"):
                            with st.spinner("Analyzing content..."):
                                metadata = analyze_transcript_metadata(transcript['processed_content'])
                                if metadata:
                                    save_transcript_metadata(transcript['id'], metadata)
                                    st.success("Metadata generated successfully!")
                                    st.rerun()

else:
    st.info("No transcripts have been processed yet.")


# Modify the transcript processing logic to generate and store embeddings and metadata



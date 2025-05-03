from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from app.processor import detect_and_process, analyze_transcript_metadata, generate_post_ideas
from app.database import (
    save_transcript, get_all_transcripts, get_transcript, get_transcript_metadata, update_transcript,
    delete_transcript, save_post_ideas, get_post_ideas, delete_post_ideas,
    log_analytics_event, get_analytics_summary, save_transcript_metadata
)
import os

app = FastAPI()

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    add_paragraphs: bool = Form(True),
    add_headings: bool = Form(True),
    fix_grammar: bool = Form(True),
    highlight_key_points: bool = Form(True),
    format_style: str = Form("Article"),
    rewrite_options: str = Form(""),
    uniqueness_level: float = Form(0.3)
):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    content = await file.read()
    is_binary = ext == ".pdf"
    if not is_binary:
        content = content.decode("utf-8")
    # Parse rewrite_options if sent as comma-separated string
    rewrite_opts = [opt.strip() for opt in rewrite_options.split(",") if opt.strip()] if rewrite_options else []
    processed = detect_and_process(
        content, filename, add_paragraphs, add_headings, fix_grammar, highlight_key_points,
        format_style, is_binary=is_binary, rewrite_options=rewrite_opts, temperature=uniqueness_level
    )
    transcript_id = save_transcript(filename, content, processed, format_style)
    metadata = analyze_transcript_metadata(processed)
    save_transcript_metadata(transcript_id, metadata)
    return JSONResponse({
        "transcript_id": transcript_id,
        "processed_content": processed,
        "original_content": content,
        "metadata": metadata
    })

@app.post("/process_text/")
async def process_text(request: Request):
    data = await request.json()
    text = data.get("text", "")
    title = data.get("title", "Untitled")
    add_paragraphs = data.get("add_paragraphs", True)
    add_headings = data.get("add_headings", True)
    fix_grammar = data.get("fix_grammar", True)
    highlight_key_points = data.get("highlight_key_points", True)
    format_style = data.get("format_style", "Article")
    rewrite_options = data.get("rewrite_options", [])
    uniqueness_level = data.get("uniqueness_level", 0.3)
    processed = detect_and_process(
        text, title, add_paragraphs, add_headings, fix_grammar, highlight_key_points,
        format_style, is_binary=False, rewrite_options=rewrite_options, temperature=uniqueness_level
    )
    transcript_id = save_transcript(title, text, processed, format_style, source_type="pasted")
    metadata = analyze_transcript_metadata(processed)
    save_transcript_metadata(transcript_id, metadata)
    return JSONResponse({
        "transcript_id": transcript_id,
        "processed_content": processed,
        "metadata": metadata
    })

@app.get("/transcripts/")
def list_transcripts():
    return get_all_transcripts()

@app.get("/transcript/{transcript_id}")
def get_transcript_detail(transcript_id: int):
    transcript = get_transcript(transcript_id)
    metadata = get_transcript_metadata(transcript_id)
    return {"transcript": transcript, "metadata": metadata}

@app.patch("/transcript/{transcript_id}")
async def update_transcript_content(transcript_id: int, request: Request):
    data = await request.json()
    processed_content = data.get("processed_content")
    if not processed_content:
        raise HTTPException(status_code=400, detail="processed_content is required")
    transcript = get_transcript(transcript_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    update_transcript(transcript_id, processed_content)
    return {"success": True}

@app.delete("/transcript/{transcript_id}")
def delete_transcript_api(transcript_id: int):
    ok = delete_transcript(transcript_id)
    return {"success": ok}

# --- Post Ideas Endpoints ---
@app.get("/post_ideas/{transcript_id}")
def get_post_ideas_api(transcript_id: int):
    ideas = get_post_ideas(transcript_id)
    return ideas or ""

@app.patch("/post_ideas/{transcript_id}")
async def update_post_ideas_api(transcript_id: int, request: Request):
    data = await request.json()
    post_ideas = data.get("post_ideas", "")
    ok = save_post_ideas(transcript_id, post_ideas)
    return {"success": ok}

@app.delete("/post_ideas/{transcript_id}")
def delete_post_ideas_api(transcript_id: int):
    ok = delete_post_ideas(transcript_id)
    return {"success": ok}

@app.post("/generate_post_ideas/")
async def generate_post_ideas_api(request: Request):
    data = await request.json()
    processed_content = data.get("processed_content", "")
    ideas = generate_post_ideas(processed_content)
    return {"post_ideas": ideas}

# --- Metadata Endpoints ---
@app.get("/metadata/{transcript_id}")
def get_metadata_api(transcript_id: int):
    metadata = get_transcript_metadata(transcript_id)
    return metadata or {}

@app.post("/analyze_metadata/")
async def analyze_metadata_api(request: Request):
    data = await request.json()
    processed_content = data.get("processed_content", "")
    metadata = analyze_transcript_metadata(processed_content)
    return metadata

# --- Analytics Endpoint ---
@app.get("/analytics/")
def analytics_api():
    return get_analytics_summary()

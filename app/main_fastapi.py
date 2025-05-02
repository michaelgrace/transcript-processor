from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from app.processor import detect_and_process, analyze_transcript_metadata
from app.database import save_transcript, get_all_transcripts, get_transcript, get_transcript_metadata, update_transcript
import os

app = FastAPI()

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    add_paragraphs: bool = Form(True),
    add_headings: bool = Form(True),
    fix_grammar: bool = Form(True),
    highlight_key_points: bool = Form(True),
    format_style: str = Form("Article")
):
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    content = await file.read()
    is_binary = ext == ".pdf"
    if not is_binary:
        content = content.decode("utf-8")
    processed = detect_and_process(
        content, filename, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style, is_binary=is_binary
    )
    transcript_id = save_transcript(filename, content, processed, format_style)
    metadata = analyze_transcript_metadata(processed)
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
def update_transcript_content(transcript_id: int, data: dict):
    processed_content = data.get("processed_content")
    if not processed_content:
        raise HTTPException(status_code=400, detail="processed_content is required")
    transcript = get_transcript(transcript_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    # Update processed_content in DB
    update_transcript(transcript_id, processed_content)
    return {"success": True}

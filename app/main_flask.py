from flask import Flask, request, jsonify
from processor import detect_and_process, analyze_transcript_metadata
from database import save_transcript, get_all_transcripts, get_transcript, get_transcript_metadata
import os

app = Flask(__name__)

@app.route("/upload/", methods=["POST"])
def upload_file():
    file = request.files["file"]
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    content = file.read()
    is_binary = ext == ".pdf"
    if not is_binary:
        content = content.decode("utf-8")
    add_paragraphs = request.form.get("add_paragraphs", "true") == "true"
    add_headings = request.form.get("add_headings", "true") == "true"
    fix_grammar = request.form.get("fix_grammar", "true") == "true"
    highlight_key_points = request.form.get("highlight_key_points", "true") == "true"
    format_style = request.form.get("format_style", "Article")
    processed = detect_and_process(
        content, filename, add_paragraphs, add_headings, fix_grammar, highlight_key_points, format_style, is_binary=is_binary
    )
    transcript_id = save_transcript(filename, content, processed, format_style)
    metadata = analyze_transcript_metadata(processed)
    return jsonify({
        "transcript_id": transcript_id,
        "processed_content": processed,
        "metadata": metadata
    })

@app.route("/transcripts/", methods=["GET"])
def list_transcripts():
    return jsonify(get_all_transcripts())

@app.route("/transcript/<int:transcript_id>", methods=["GET"])
def get_transcript_detail(transcript_id):
    transcript = get_transcript(transcript_id)
    metadata = get_transcript_metadata(transcript_id)
    return jsonify({"transcript": transcript, "metadata": metadata})

if __name__ == "__main__":
    import os
    port = int(os.getenv("FLASK_PORT", 9001))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import requests
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

API_URL = os.getenv("API_URL", "http://api:8000")

@app.route("/", methods=["GET", "POST"])
def index():
    processed_content = None
    original_content = None
    filename = None
    metadata = None
    transcript_id = None

    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        content = file.read()
        is_binary = ext == ".pdf"
        if not is_binary:
            content = content.decode("utf-8")
        # Get formatting options from form
        add_paragraphs = "add_paragraphs" in request.form
        add_headings = "add_headings" in request.form
        fix_grammar = "fix_grammar" in request.form
        highlight_key_points = "highlight_key_points" in request.form
        format_style = request.form.get("format_style", "Article")
        # Send to API for processing and saving
        resp = requests.post(
            f"{API_URL}/upload/",
            files={"file": (filename, content.encode("utf-8") if not is_binary else content)},
            data={
                "add_paragraphs": str(add_paragraphs).lower(),
                "add_headings": str(add_headings).lower(),
                "fix_grammar": str(fix_grammar).lower(),
                "highlight_key_points": str(highlight_key_points).lower(),
                "format_style": format_style,
            },
        )
        if resp.ok:
            data = resp.json()
            processed_content = data.get("processed_content")
            transcript_id = data.get("transcript_id")
            metadata = data.get("metadata")
            original_content = content if not is_binary else "[PDF Uploaded]"
            flash("Processing complete!", "success")
        else:
            flash("API error: could not process file", "danger")
    elif request.method == "GET" and request.args.get("transcript_id"):
        transcript_id = int(request.args.get("transcript_id"))
        resp = requests.get(f"{API_URL}/transcript/{transcript_id}")
        if resp.ok:
            data = resp.json()
            transcript = data.get("transcript")
            processed_content = transcript.get("processed_content")
            original_content = transcript.get("original_content")
            filename = transcript.get("filename")
            metadata = data.get("metadata")
        else:
            flash("Transcript not found.", "danger")
    # List all transcripts
    resp = requests.get(f"{API_URL}/transcripts/")
    transcripts = resp.json() if resp.ok else []
    return render_template(
        "index.html",
        processed_content=processed_content,
        original_content=original_content,
        filename=filename,
        metadata=metadata,
        transcripts=transcripts,
        transcript_id=transcript_id
    )

@app.route("/save_processed/<int:transcript_id>", methods=["POST"])
def save_processed(transcript_id):
    new_content = request.form.get("processed_content", "")
    # Update via API (assumes you add a PATCH or PUT endpoint to your API)
    resp = requests.patch(
        f"{API_URL}/transcript/{transcript_id}",
        json={"processed_content": new_content}
    )
    if resp.ok:
        flash("Processed content updated!", "success")
    else:
        flash("Failed to update transcript.", "danger")
    return redirect(url_for("index", transcript_id=transcript_id))

@app.route("/download_processed/<int:transcript_id>")
def download_processed(transcript_id):
    resp = requests.get(f"{API_URL}/transcript/{transcript_id}")
    if not resp.ok:
        flash("Transcript not found.", "danger")
        return redirect(url_for("index"))
    transcript = resp.json().get("transcript")
    filename = transcript.get("filename") or "processed_content.txt"
    processed_content = transcript.get("processed_content") or ""
    response = make_response(processed_content)
    response.headers["Content-Disposition"] = f"attachment; filename={filename.rsplit('.',1)[0]}_processed.md"
    response.mimetype = "text/markdown"
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9001, debug=True)

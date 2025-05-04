# Transcript Processor

A powerful tool for transforming raw transcripts into well-structured, readable documents with AI assistance.

## Description

Transcript Processor is an AI-powered application designed to process spoken word transcripts efficiently. It automatically converts subtitle files (SRT) or raw text transcripts into well-formatted documents with proper sentence structure, paragraphs, and headings while preserving the natural flow of speech. This tool simplifies the often tedious process of transcript cleanup and formatting, making content more accessible and easier to analyze.

## Features

- **Multiple File Format Support**: Process both SRT subtitle files and plain text transcripts
- **AI-Powered Formatting**: Utilizes OpenAI GPT models to intelligently format content
- **Customizable Document Structure**: Options for paragraph organization, headings, and formatting styles
- **Grammar Correction**: Automatically fixes punctuation and grammar issues
- **Key Point Highlighting**: Identifies and emphasizes important points in the text
- **Multiple Output Styles**: Format documents as articles, transcripts, meeting notes, or academic papers
- **Markdown Output**: Generates clean, properly formatted Markdown for easy use in documentation
- **Interactive Web Interface**: User-friendly Streamlit UI for easy processing
- **Docker Support**: Run anywhere with containerized deployment

## Installation

### Prerequisites
- Docker and Docker Compose
- Git
- OpenAI API key

### Setup Instructions

1. **Clone the repository**
   ```powershell
   git clone https://github.com/yourusername/transcript-processor.git
   cd transcript-processor
   ```

2. **Create environment file**
   ```powershell
   # Create a .env file with your OpenAI API key
   echo "API_KEY=your_openai_api_key" > .env
   echo "AI_MODEL=gpt-4" >> .env
   ```

3. **Build and run with Docker**
   ```powershell
   docker-compose up --build
   ```

4. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## Usage

### Processing Transcripts

1. Open the application in your browser
2. Choose formatting options in the "Formatting Options" section:
   - Paragraph Structure
   - Add Headings for Topics
   - Fix Grammar & Punctuation
   - Highlight Key Points
   - Select a Document Style (Article, Transcript, Meeting Notes, Academic)
3. Upload your SRT or text file using the file uploader
4. View the processed content in the "Processed Content" tab
5. Download the formatted Markdown file using the "Download Markdown" button

### Example Docker Commands

**Start the application:**
```powershell
docker-compose up
```

**Rebuild after code changes:**
```powershell
docker-compose up --build
```

**Stop the application:**
```powershell
docker-compose down
```

---

# Docker Build Error: `archive/tar: unknown file mode ?rwxr-xr-x`

---

## **What This Means**

- This error occurs when Docker tries to build an image and encounters a file or directory with an **unsupported or corrupt file mode** (permissions/attributes) in your build context.
- It often happens when copying files from Windows to WSL2, or when there are symlinks, special files, or permission issues in your project directory.

---

## **How to Fix**

1. **Check for problematic files:**
   - Run this in your project directory (in WSL2):
     ```sh
     find . -type l
     ```
   - This lists all symlinks. Remove any broken or unnecessary symlinks.

2. **Check for files with odd permissions:**
   - Run:
     ```sh
     find . -exec ls -l {} \; | grep '^?'
     ```
   - This lists files with unknown or corrupt permissions. Remove or fix them.

3. **Clean up your build context:**
   - Make sure you do **not** have `node_modules`, `.venv`, `.next`, or other large/binary folders in your build context.  
   - These should be in your `.gitignore` and ideally in your `.dockerignore` as well.

4. **Add a `.dockerignore` file** (if you don't have one) to exclude unnecessary files from the build context:
   ```
   node_modules
   .next
   .venv
   __pycache__
   *.pyc
   .git
   .DS_Store
   ```
   - Place this file in your project root.

5. **Try the build again:**
   ```sh
   docker-compose build --no-cache
   ```

---

## **Summary**

- The error is caused by a file with an unsupported or corrupt mode in your build context.
- Clean up symlinks, fix permissions, and use a `.dockerignore` to exclude unnecessary files.
- This will make your build faster and more reliable.

---

**If you still see the error after these steps, let me know what files are listed by the `find` commands above.**

---

## Contributing

Contributions are welcome! Here's how you can contribute to the project:

1. **Fork the repository**
2. **Create a feature branch**
   ```powershell
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```powershell
   git commit -m 'Add some amazing feature'
   ```
4. **Push to your branch**
   ```powershell
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

Please ensure your code follows the project's style guidelines and includes appropriate tests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [OpenAI](https://openai.com/) GPT models
- Uses [pysrt](https://github.com/byroot/pysrt) for SRT file processing

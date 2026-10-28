# Diagram2Doc — Local React + FastAPI dashboard

A local app for uploading an architecture diagram, extracting text with Tesseract OCR, detecting likely component categories, generating a Markdown documentation draft, and downloading it.

## Requirements
- Windows 10/11
- Python 3.10+ (Python 3.12 recommended)
- Node.js 20+
- Tesseract OCR installed locally

## Install Tesseract
Install the Windows Tesseract OCR engine and add its installation folder to PATH (often `C:\Program Files\Tesseract-OCR`). Open a new PowerShell and verify `tesseract --version`. If PATH is not configured, add this line to `backend/main.py` after imports:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## Start backend (PowerShell terminal 1)
From the project root:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend health: http://127.0.0.1:8000/api/health
API docs: http://127.0.0.1:8000/docs

## Start frontend (PowerShell terminal 2)
From the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173.

## Workflow
1. Upload PNG, JPG/JPEG, or WEBP (maximum 10 MB).
2. Click **Analyze diagram**.
3. Review OCR labels and likely component categories.
4. Switch documentation tabs and download Markdown.

## Important scope note
This is a functional local starter for OCR → heuristic component labels → template-based documentation → Markdown export. It does **not yet** load the Colab LLM, Sentence Transformer, or FAISS index. The reference search in the UI searches current OCR/documentation text, not semantic RAG. Arrow direction and component relationships are not inferred automatically. To reuse the exact Colab pipeline, export and adapt the Python processing functions and reference data into backend modules; large model weights may be too heavy for some computers.

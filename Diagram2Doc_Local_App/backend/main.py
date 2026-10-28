from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image
from pathlib import Path
from datetime import datetime
import pytesseract, io, re
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI(title='Diagram2Doc API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['http://127.0.0.1:5173','http://localhost:5173'], allow_methods=['*'], allow_headers=['*'])
MAX_BYTES = 10 * 1024 * 1024
ALLOWED = {'image/png','image/jpeg','image/webp'}
PATTERNS = {
 'Client / User': r'\b(client|user|browser|mobile)\b', 'Load Balancer': r'\b(load.?balancer|alb|elb)\b',
 'Web Server': r'\b(web.?server|nginx|apache)\b', 'Application Server': r'\b(app(lication)?.?server|backend.?server)\b',
 'Database': r'\b(database|mysql|postgres(?:ql)?|rds|mongodb|sql)\b', 'Cache': r'\b(cache|redis|memcached)\b',
 'Object Storage': r'\b(object.?storage|s3|blob.?storage)\b', 'API / Microservice': r'\b(api|microservice|service)\b',
 'Queue / Messaging': r'\b(queue|kafka|rabbitmq|sqs|sns)\b', 'Monitoring / Logging': r'\b(monitoring|logging|cloudwatch|prometheus|grafana)\b',
 'Authentication': r'\b(auth|identity|oauth|jwt|cognito)\b', 'CDN': r'\b(cdn|cloudfront)\b'
}

def detect(text):
    components = [name for name, pattern in PATTERNS.items() if re.search(pattern, text.lower())]
    labels = [re.sub(r'\s+', ' ', line).strip(' •-\t') for line in text.splitlines()]
    return components, [x for x in labels if 2 < len(x) < 120][:100]

def make_docs(filename, components, labels):
    comps = '\n'.join(f'- **{c}** — detected heuristically from OCR; verify against the diagram.' for c in components) or '- No known component categories confidently detected.'
    labs = '\n'.join(f'- {x}' for x in labels) or '- No text labels detected.'
    return f'''# Diagram2Doc Architecture Documentation\n\n> Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}. OCR-assisted draft; verify against the source image.\n\n## 1. Overview\n\nThis draft summarizes text extracted from **{filename}** and identifies likely component categories. OCR alone does not establish all connections or arrow directions.\n\n## 2. Detected component categories\n\n{comps}\n\n## 3. OCR labels\n\n{labs}\n\n## 4. Architecture flow\n\nReview the original diagram to confirm request flow, data flow, arrow directions, and trust boundaries.\n\n## 5. Reliability considerations\n\n- Check redundancy and single points of failure.\n- Verify health checks, timeouts, retries, backups, and recovery.\n- Confirm load balancing and scaling behavior.\n\n## 6. Security considerations\n\n- Verify authentication and authorization boundaries.\n- Confirm TLS, secret management, least privilege, and encryption requirements.\n- Review network exposure and sensitive-data logging.\n\n## 7. Limitations\n\n- OCR may omit, merge, or misread labels.\n- Component categories are heuristic matches.\n- Relationships and arrow directions require visual verification.\n- This local starter uses a conservative template, not the Colab LLM/FAISS index.\n'''

@app.get('/api/health')
def health(): return {'status':'ok','service':'Diagram2Doc API'}

@app.post('/api/analyze')
async def analyze(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED: raise HTTPException(415, 'Upload a PNG, JPG, or WEBP image.')
    raw = await file.read()
    if not raw: raise HTTPException(400, 'The uploaded file is empty.')
    if len(raw) > MAX_BYTES: raise HTTPException(413, 'Image exceeds the 10 MB limit.')
    try: image = Image.open(io.BytesIO(raw)).convert('RGB')
    except Exception: raise HTTPException(400, 'Could not read image. Try another PNG or JPEG.')
    try: text = pytesseract.image_to_string(image).strip()
    except pytesseract.TesseractNotFoundError: raise HTTPException(503, 'Tesseract OCR is not installed or is missing from PATH. See README.md.')
    components, labels = detect(text)
    return {'filename':file.filename, 'image_width':image.width, 'image_height':image.height, 'ocr_text':text, 'components':components, 'labels':labels, 'documentation':make_docs(file.filename or 'architecture image',components,labels), 'warnings':['OCR labels may be noisy.','Component relationships and arrow directions are not inferred automatically.']}

@app.post('/api/export')
async def export(payload: dict):
    text = payload.get('documentation','')
    if not isinstance(text,str) or not text.strip(): raise HTTPException(400,'No documentation provided.')
    name = re.sub(r'[^A-Za-z0-9_.-]+','-',str(payload.get('filename','diagram2doc-documentation.md')))[:80]
    if not name.endswith('.md'): name += '.md'
    return Response(text, media_type='text/markdown; charset=utf-8', headers={'Content-Disposition':f'attachment; filename="{name}"'})

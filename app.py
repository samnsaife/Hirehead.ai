# app.py
import os
import re
import io
import joblib
import uvicorn
import traceback
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ML / NLP
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# File parsing (PDF/DOCX/TXT)
from pdfminer.high_level import extract_text as pdf_extract_text
from docx import Document

# --- Constants / Paths ---
DATA_PATH = "data/resume_dataset.csv"
MODELS_DIR = "models"
VECTORIZER_PATH = os.path.join(MODELS_DIR, "tfidf.joblib")
MODEL_PATH = os.path.join(MODELS_DIR, "clf.joblib")

os.makedirs(MODELS_DIR, exist_ok=True)

# --- FastAPI app ---
app = FastAPI(
    title="Resume Bot (ATS Analyzer)",
    description="Scores resumes, suggests keywords, and gives ATS + formatting feedback.",
    version="1.0.0",
)

# Open CORS so your Next.js can call it from anywhere in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# ---------- Utilities ----------

SECTION_HINTS = [
    "summary", "objective", "education", "experience", "work experience",
    "projects", "skills", "certifications", "awards", "achievements",
    "contact", "publications", "courses", "volunteer"
]

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3,5}\)?[-.\s]?)\d{3,4}[-.\s]?\d{3,4}")

def clean_text(t: str) -> str:
    if not t:
        return ""
    return re.sub(r"\s+", " ", t).strip().lower()

def simple_tokenize(t: str) -> List[str]:
    t = re.sub(r"[^a-z0-9+.# ]", " ", t.lower())
    return [w for w in t.split() if w]

def guess_skills(tokens: List[str]) -> List[str]:
    # a light skills lexicon you can expand later
    SKILL_BANK = {
        "python","java","javascript","typescript","react","node","nextjs",
        "mongodb","postgresql","mysql","docker","kubernetes","aws","gcp","azure",
        "linux","git","tensorflow","pytorch","sklearn","nlp","opencv","html","css",
        "flask","django","fastapi","rest","microservices","ci","cd","jenkins",
        "redis","graphql","tailwind","c++","c","bash","powershell","matlab",
        "r","pandas","numpy","matplotlib","jira","agile","spark","hadoop"
    }
    found = sorted(list(SKILL_BANK.intersection(set(tokens))))
    return found

def extract_text_from_upload(upload: UploadFile) -> str:
    content = upload.file.read()
    name = upload.filename.lower()

    if name.endswith(".pdf"):
        # pdfminer wants a file-like object; use bytes buffer
        return pdf_extract_text(io.BytesIO(content)) or ""
    elif name.endswith(".docx"):
        buf = io.BytesIO(content)
        doc = Document(buf)
        return "\n".join([p.text for p in doc.paragraphs])
    elif name.endswith(".txt"):
        try:
            return content.decode("utf-8", errors="ignore")
        except Exception:
            return content.decode("latin-1", errors="ignore")
    else:
        # default: try utf-8 text
        try:
            return content.decode("utf-8", errors="ignore")
        except Exception:
            return content.decode("latin-1", errors="ignore")

def load_dataset() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    # expected cols: ["text", "label"] where label in {"good","bad"}
    df["text"] = df["text"].fillna("").astype(str)
    df["label"] = df["label"].fillna("bad").astype(str)
    return df

def train_and_save() -> Dict[str, Any]:
    df = load_dataset()

    vectorizer = TfidfVectorizer(
        min_df=1,
        max_df=0.95,
        ngram_range=(1,2),
        stop_words="english"
    )
    X = vectorizer.fit_transform(df["text"].values)
    y = (df["label"].str.strip().str.lower() == "good").astype(int).values

    clf = LogisticRegression(max_iter=200)
    clf.fit(X, y)

    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(clf, MODEL_PATH)

    acc = float(clf.score(X, y))
    return {"train_samples": len(df), "train_accuracy_on_small_set": acc}

def ensure_model():
    """Load or train initial model from bundled dataset."""
    if os.path.exists(VECTORIZER_PATH) and os.path.exists(MODEL_PATH):
        return
    train_and_save()

def load_model():
    ensure_model()
    vectorizer = joblib.load(VECTORIZER_PATH)
    clf = joblib.load(MODEL_PATH)
    return vectorizer, clf

def ats_heuristics(resume_text: str) -> Dict[str, Any]:
    text = resume_text
    lowered = resume_text.lower()

    # Contact info
    emails = EMAIL_RE.findall(text)
    phones = PHONE_RE.findall(text)
    phone_found = bool(phones)
    email_found = bool(emails)

    # Bullet / formatting hints (simple proxies)
    has_bullets = any(b in text for b in ["•", "-", "–", "*"])
    char_len = len(text)
    word_len = len(text.split())

    # Section checks
    section_presence = {sec: (sec in lowered) for sec in SECTION_HINTS}
    sections_ok = sum(section_presence.values())

    # Simple length guidance
    length_feedback = "OK"
    if word_len < 200:
        length_feedback = "Too short for a complete resume."
    elif word_len > 1200:
        length_feedback = "Too long; consider trimming to 1–2 pages."

    # Score (0-100): base on sections + contact + bullets + length signal
    score = 40 + (sections_ok * 4)
    if email_found: score += 5
    if phone_found: score += 5
    if has_bullets: score += 6
    # light penalty for extreme lengths
    if word_len < 150 or word_len > 1400:
        score -= 6
    score = int(max(0, min(100, score)))

    formatting = []
    if not email_found: formatting.append("Add a professional email.")
    if not phone_found: formatting.append("Add a reachable phone number.")
    if not has_bullets: formatting.append("Use bullet points for achievements.")
    if sections_ok < 4: formatting.append("Add core sections (Summary, Skills, Experience, Education).")

    return {
        "email_found": email_found,
        "phone_found": phone_found,
        "has_bullets": has_bullets,
        "char_length": char_len,
        "word_length": word_len,
        "length_feedback": length_feedback,
        "section_presence": section_presence,
        "heuristic_score": score,
        "formatting_feedback": formatting
    }

def keywords_from_job_description(job_description: str, top_k: int = 15) -> List[str]:
    tokens = simple_tokenize(job_description)
    # naive TF scoring
    tf = {}
    for t in tokens:
        if len(t) <= 2: 
            continue
        tf[t] = tf.get(t, 0) + 1
    # sort by freq
    ranked = sorted(tf.items(), key=lambda x: (-x[1], x[0]))
    return [w for w, c in ranked[:top_k]]

def missing_keywords(resume_tokens: List[str], jd_keywords: List[str]) -> List[str]:
    rset = set(resume_tokens)
    miss = [kw for kw in jd_keywords if kw not in rset]
    # filter obvious noise
    noisy = {"with","and","for","the","you","your","our","work","team"}
    return [kw for kw in miss if kw not in noisy]

# ---------- Pydantic Schemas ----------
class TrainResponse(BaseModel):
    train_samples: int
    train_accuracy_on_small_set: float

class AnalyzeRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = None
    target_role: Optional[str] = None

class AnalyzeResponse(BaseModel):
    classification: str
    probability_good: float
    ats_score: int
    heuristics: Dict[str, Any]
    skills_detected: List[str]
    top_resume_keywords: List[str]
    suggested_keywords_from_jd: List[str]
    missing_keywords_vs_jd: List[str]
    notes: List[str]

# ---------- Startup: ensure model ----------
ensure_model()

# ---------- Endpoints ----------

@app.get("/")
def health():
    return {"status": "ok", "message": "Resume Bot API running"}

@app.post("/train", response_model=TrainResponse)
def train():
    """
    Retrain from data/resume_dataset.csv and overwrite model artifacts.
    """
    result = train_and_save()
    return TrainResponse(**result)

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    """
    Analyze resume text, return ML classification + ATS heuristics + keyword tips.
    """
    vectorizer, clf = load_model()

    text = req.resume_text or ""
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])
    proba = clf.predict_proba(X)[0][1] if hasattr(clf, "predict_proba") else float(clf.decision_function(X)[0])
    prob_good = float(max(0.0, min(1.0, proba)))  # clamp
    pred = clf.predict(X)[0]
    classification = "good" if int(pred) == 1 else "bad"

    heur = ats_heuristics(text)
    tokens_resume = simple_tokenize(text)
    skills = guess_skills(tokens_resume)

    # keywords on resume via tf-idf vocabulary (top weighted features for this doc)
    feature_names = np.array(vectorizer.get_feature_names_out())
    row = X.toarray()[0]
    idx_sorted = np.argsort(-row)[:15]
    top_resume_kw = [feature_names[i] for i in idx_sorted if row[i] > 0][:15]

    jd_kw = []
    missing_vs_jd = []
    if req.job_description:
        jd_kw = keywords_from_job_description(req.job_description, top_k=15)
        missing_vs_jd = missing_keywords(tokens_resume, jd_kw)

    # combine ATS heuristics score with ML confidence for a final 0-100
    ats_score = int(0.6 * heur["heuristic_score"] + 0.4 * (prob_good * 100))
    ats_score = max(0, min(100, ats_score))

    notes = []
    if req.target_role:
        notes.append(f"Optimizing for target role: {req.target_role}")
    if req.job_description and missing_vs_jd:
        notes.append("Consider adding some of the missing keywords from the JD if relevant.")

    return AnalyzeResponse(
        classification=classification,
        probability_good=prob_good,
        ats_score=ats_score,
        heuristics=heur,
        skills_detected=skills,
        top_resume_keywords=top_resume_kw,
        suggested_keywords_from_jd=jd_kw,
        missing_keywords_vs_jd=missing_vs_jd,
        notes=notes
    )

@app.post("/analyze-file", response_model=AnalyzeResponse)
async def analyze_file(
    file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    target_role: Optional[str] = Form(None)
):
    """
    Upload a resume file (PDF/DOCX/TXT). Parses text and forwards to /analyze logic.
    """
    try:
        text = extract_text_from_upload(file)
    except Exception:
        traceback.print_exc()
        text = ""

    req = AnalyzeRequest(resume_text=text, job_description=job_description, target_role=target_role)
    return analyze(req)

if __name__ == "__main__":
    # Local dev: uvicorn app:app --reload
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

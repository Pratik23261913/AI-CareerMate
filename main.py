import re

import fitz  # PyMuPDF
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ==========================================
# 1. CREATE FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="AI CareerMate API",
    description="Resume Analysis and Job Match Analysis API",
    version="1.0.0",
)


# ==========================================
# 2. CONFIGURE CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://pratik23261913.github.io",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 3. SKILLS DATABASE
# ==========================================

SKILLS_LIST = [
    "Python",
    "Java",
    "C",
    "C++",
    "SQL",
    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Node.js",
    "FastAPI",
    "Django",
    "MySQL",
    "MongoDB",
    "Git",
    "GitHub",
    "Excel",
    "Machine Learning",
    "Data Analysis",
    "REST API",
    "Communication",
    "Problem Solving",
]


# ==========================================
# 4. EXTRACT SKILLS
# ==========================================

def extract_skills(text: str) -> list:
    """
    Find recognized skills in the provided text.
    """

    found_skills = []
    text_lower = text.lower()

    for skill in SKILLS_LIST:
        pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return found_skills


# ==========================================
# 5. CALCULATE RESUME COMPLETENESS SCORE
# ==========================================

def calculate_resume_score(
    resume_text: str,
    skills: list,
) -> dict:
    """
    Calculate a basic rule-based resume completeness score.

    This is not an assessment of employability.
    """

    text = resume_text.lower()

    # Technical skills: maximum 30 points
    technical_score = min(len(skills) * 5, 30)

    # Education: maximum 20 points
    education_keywords = [
        "education",
        "bachelor",
        "degree",
        "b.sc",
        "bsc",
        "b.tech",
        "computer science",
        "university",
        "college",
    ]

    education_score = (
        20
        if any(keyword in text for keyword in education_keywords)
        else 0
    )

    # Projects: maximum 20 points
    project_keywords = [
        "project",
        "projects",
        "developed",
        "application",
        "website",
        "system",
    ]

    project_score = (
        20
        if any(keyword in text for keyword in project_keywords)
        else 0
    )

    # Certifications: maximum 15 points
    certification_keywords = [
        "certification",
        "certifications",
        "certificate",
        "certificates",
    ]

    certification_score = (
        15
        if any(keyword in text for keyword in certification_keywords)
        else 0
    )

    # Contact information: maximum 15 points
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    phone_pattern = r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)"

    has_email = bool(re.search(email_pattern, resume_text))
    has_phone = bool(re.search(phone_pattern, resume_text))

    contact_score = 0

    if has_email:
        contact_score += 8

    if has_phone:
        contact_score += 7

    total_score = (
        technical_score
        + education_score
        + project_score
        + certification_score
        + contact_score
    )

    suggestions = []

    if technical_score < 30:
        suggestions.append(
            "Add relevant technical skills that accurately reflect your abilities."
        )

    if education_score == 0:
        suggestions.append(
            "Add an Education section with your degree and institution."
        )

    if project_score == 0:
        suggestions.append(
            "Add projects describing what you built and which technologies you used."
        )

    if certification_score == 0:
        suggestions.append(
            "Include relevant certifications if you have completed any."
        )

    if not has_email:
        suggestions.append(
            "Add a professional email address."
        )

    if not has_phone:
        suggestions.append(
            "Add a valid contact phone number."
        )

    if not suggestions:
        suggestions.append(
            "Your resume includes all five checked categories. Review it for accuracy and clarity."
        )

    return {
        "score": total_score,
        "maximum_score": 100,
        "breakdown": {
            "technical_skills": technical_score,
            "education": education_score,
            "projects": project_score,
            "certifications": certification_score,
            "contact_information": contact_score,
        },
        "suggestions": suggestions,
    }


# ==========================================
# 6. HOME ROUTE
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Welcome to AI CareerMate API",
        "features": [
            "Resume Analysis",
            "Job Match Analysis",
        ],
        "status": "running",
    }


# ==========================================
# 7. HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }


# ==========================================
# 8. RESUME UPLOAD AND ANALYSIS
# ==========================================

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a PDF resume and analyze its extracted text.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a PDF file.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Read at most 5 MB + 1 byte to enforce the limit
    content = await file.read(5 * 1024 * 1024 + 1)

    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="The resume must be 5 MB or smaller.",
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="The uploaded file does not appear to be a valid PDF.",
        )

    try:
        with fitz.open(stream=content, filetype="pdf") as pdf:
            resume_text = "\n".join(
                page.get_text()
                for page in pdf
            )

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Please try another PDF file.",
        )

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found in this PDF. "
                "Please upload a text-based PDF resume."
            ),
        )

    skills = extract_skills(resume_text)

    resume_score = calculate_resume_score(
        resume_text,
        skills,
    )

    return {
        "message": "Resume analysis completed!",
        "filename": file.filename,
        "size_bytes": len(content),
        "skills": skills,
        "skills_count": len(skills),
        "resume_score": resume_score,
        "status": "success",
    }


# ==========================================
# 9. JOB MATCH REQUEST MODEL
# ==========================================

class JobMatchRequest(BaseModel):
    resume_skills: str
    job_description: str


# ==========================================
# 10. JOB MATCH ANALYSIS
# ==========================================

@app.post("/job-match")
def job_match(request: JobMatchRequest):
    """
    Compare resume skills with skills identified in a job description.
    """

    if not request.resume_skills.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter your resume skills.",
        )

    if not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a job description.",
        )

    # Identify skills in each input
    resume_skills = extract_skills(request.resume_skills)

    required_skills = extract_skills(
        request.job_description
    )

    # Find skills appearing in both lists
    matched_skills = [
        skill
        for skill in required_skills
        if skill in resume_skills
    ]

    # Find required skills not detected in the resume
    missing_skills = [
        skill
        for skill in required_skills
        if skill not in resume_skills
    ]

    # Calculate the skills match percentage
    total_required = len(required_skills)

    if total_required == 0:
        match_percentage = 0
    else:
        match_percentage = round(
            len(matched_skills) / total_required * 100
        )

    # Generate recommendations
    recommendations = [
        f"Learn or practise {skill} to improve your match for this job."
        for skill in missing_skills
    ]

    if total_required == 0:
        recommendations.append(
            "No recognized skills were found in the job description. "
            "Try including specific technical skills such as Python, SQL, or Git."
        )

    elif not missing_skills:
        recommendations.append(
            "All detected required skills match. "
            "Review the complete job description for other requirements."
        )

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_required_skills": total_required,
        "matched_skills_count": len(matched_skills),
        "match_percentage": match_percentage,
        "recommendations": recommendations,
        "status": "success",
    }
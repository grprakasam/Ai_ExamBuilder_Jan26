from fastapi import APIRouter, Depends, HTTPException, Request
from app.api import deps
from app.models.exam_attempt import ExamAttempt
from app.services.scoring import score_questions
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.test import Test, Question
from app.services.pdf_service import PDFService
import uuid
import os
import tempfile

router = APIRouter()

@router.get("/{test_id}/download")
async def download_test_pdf(
    test_id: uuid.UUID,
    access=Depends(deps.require_test_access),
    db: Session = Depends(get_db)
):
    # 1. Fetch test and questions
    db_test = db.query(Test).filter(Test.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # 2. Convert to dictionary for template
    test_dict = {
        "title": db_test.title,
        "grade_level": db_test.grade_level,
        "subject": db_test.subject,
        "standard_focus": db_test.standard_focus
    }
    
    questions_list = []
    for q in db_test.questions:
        questions_list.append({
            "sequence": q.sequence,
            "question_text": q.question_text,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "cognitive_level": q.cognitive_level
        })
    
    # 3. Generate PDF to temporary file
    pdf_service = PDFService()
    temp_dir = tempfile.gettempdir()
    file_name = f"EOG_Practice_{test_id}.pdf"
    file_path = os.path.join(temp_dir, file_name)
    
    try:
        pdf_service.generate_test_pdf(test_dict, questions_list, file_path)
        return FileResponse(
            path=file_path,
            filename=f"{db_test.title.replace(' ', '_')}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Generation failed: {str(e)}")
@router.get("/{test_id}/results/download")
async def download_results_pdf(
    test_id: uuid.UUID,
    attempt_id: uuid.UUID,
    request: Request,
    access=Depends(deps.require_test_access),
    db: Session = Depends(get_db)
):
    db_test = db.query(Test).filter(Test.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id, ExamAttempt.test_id == test_id).first()
    if not attempt or attempt.session_hash != deps.session_hash(request) or not attempt.is_completed:
        raise HTTPException(403, "Completed attempt for this session required")
    score = score_questions(db_test.questions, attempt.answers or {}, db_test.exam_standard)["score"]
    feedback = "MCQ score computed by the server. Written answers require educator review."
    test_dict = {
        "title": db_test.title,
        "grade_level": db_test.grade_level,
        "subject": db_test.subject,
        "score": score,
        "feedback": feedback,
        "date": db_test.created_at.strftime("%Y-%m-%d %H:%M") if db_test.created_at else "N/A"
    }
    
    questions_list = []
    for q in db_test.questions:
        questions_list.append({
            "question_text": q.question_text,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation
        })
    
    pdf_service = PDFService()
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"Results_{test_id}_{attempt_id}.pdf")
    
    try:
        pdf_service.generate_test_pdf(test_dict, questions_list, file_path, template_name="results_template.html")
        return FileResponse(
            path=file_path,
            filename=f"Report_{db_test.title.replace(' ', '_')}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF Generation failed: {str(e)}")

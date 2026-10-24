import uuid
from fastapi import APIRouter, Depends, Header, Request, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.services.mastery_service import MasteryService
from app.services.adaptive_difficulty import AdaptiveDifficultyService, PersonalizedPracticeQueue

router = APIRouter(prefix="/learning", tags=["learning"])

def authorize(db, test_id, code):
    return deps.authorize_test(db, test_id, code)

@router.get("/mastery/summary/{test_id}")
def summary(test_id: uuid.UUID, request: Request, db: Session = Depends(get_db), x_access_code: str = Header(...)):
    authorize(db, test_id, x_access_code)
    return MasteryService.get_mastery_summary(db, test_id, learner_key=deps.session_hash(request))

@router.get("/mastery/due-for-review/{test_id}")
def due(test_id: uuid.UUID, request: Request, db: Session = Depends(get_db), x_access_code: str = Header(...)):
    authorize(db, test_id, x_access_code)
    records = MasteryService.get_concepts_due_for_review(db, test_id, learner_key=deps.session_hash(request))
    return {"concepts_due": [{"concept_id": r.concept_id, "current_level": r.current_level,
                              "next_review_due": r.next_review_due} for r in records]}

@router.get("/adaptive/difficulty/{test_id}/{concept_id}")
def difficulty(test_id: uuid.UUID, concept_id: str, request: Request,
               db: Session = Depends(get_db), x_access_code: str = Header(...)):
    authorize(db, test_id, x_access_code)
    value = AdaptiveDifficultyService.calculate_current_difficulty(
        db, test_id, concept_id, learner_key=deps.session_hash(request))
    return {"difficulty_score": value, "difficulty_label": AdaptiveDifficultyService.get_difficulty_label(value).value}

class PracticeSessionRequest(BaseModel):
    test_id: uuid.UUID
    target_questions: int = Field(20, ge=1, le=50)
    mix_ratio: float = Field(0.7, ge=0, le=1)

@router.post("/adaptive/practice-session")
def practice(body: PracticeSessionRequest, request: Request, db: Session = Depends(get_db), x_access_code: str = Header(...)):
    authorize(db, body.test_id, x_access_code)
    queue = PersonalizedPracticeQueue.generate_practice_session(
        db, body.test_id, body.target_questions, body.mix_ratio, learner_key=deps.session_hash(request))
    return {"practice_queue": queue, "total_questions": len(queue)}

@router.get("/analytics/progress/{test_id}")
def progress(test_id: uuid.UUID, request: Request, db: Session = Depends(get_db), x_access_code: str = Header(...)):
    authorize(db, test_id, x_access_code)
    return MasteryService.get_mastery_summary(db, test_id, learner_key=deps.session_hash(request))

@router.post("/mastery/update")
def update():
    raise HTTPException(410, "Use /tests/{test_id}/practice-answer; correctness is checked on the server")

class DiagnosticRequest(BaseModel):
    grade_level: int = Field(ge=3, le=12)
    subject: str
    exam_standard: str = "ncdpi"

@router.post("/diagnostic/create")
async def create_diagnostic(body: DiagnosticRequest, db: Session = Depends(get_db)):
    from app.schemas.test import TestCreate
    from app.api.v1.tests import generate_test
    return await generate_test(TestCreate(
        title="Diagnostic practice", grade_level=body.grade_level, subject=body.subject,
        standard_focus="Foundational concepts and prerequisites", question_count=12,
        question_type="mcq", difficulty="medium", exam_standard=body.exam_standard.lower()), db)

class DiagnosticAnswers(BaseModel):
    test_id: uuid.UUID
    answers: dict[str, str]

@router.post("/diagnostic/analyze")
def analyze_diagnostic(body: DiagnosticAnswers, request: Request,
                       db: Session = Depends(get_db), x_access_code: str = Header(...)):
    from app.services.diagnostic_service import DiagnosticService
    test = authorize(db, body.test_id, x_access_code)
    # Analysis is advisory; persisted mastery uses the protected answer/submission routes.
    service = DiagnosticService.__new__(DiagnosticService)
    result = service.analyze_diagnostic_results(db, body.test_id,
                                               {int(k): v for k, v in body.answers.items()}, test.questions)
    return {"diagnostic_results": result,
            "learning_path": service.create_personalized_learning_path(db, result, test.grade_level)}

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.services.mastery_service import MasteryService
from app.services.diagnostic_service import DiagnosticService
from app.services.adaptive_difficulty import AdaptiveDifficultyService, PersonalizedPracticeQueue
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/learning", tags=["learning"])


# ===== REQUEST/RESPONSE MODELS =====

class MasteryUpdateRequest(BaseModel):
    test_id: str
    concept_id: str
    is_correct: bool
    time_taken_seconds: float
    had_hint: bool = False


class DiagnosticRequest(BaseModel):
    grade_level: int
    subject: str
    exam_standard: str = "NCDPI"


class PracticeSessionRequest(BaseModel):
    test_id: str
    target_questions: int = 20
    mix_ratio: float = 0.7


# ===== MASTERY ENDPOINTS =====

@router.post("/mastery/update")
async def update_mastery(
    request: MasteryUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update mastery record after answering a question."""
    try:
        test_id = uuid.UUID(request.test_id)
        
        record = MasteryService.update_mastery_record(
            db=db,
            test_id=test_id,
            concept_id=request.concept_id,
            is_correct=request.is_correct,
            time_taken_seconds=request.time_taken_seconds,
            had_hint=request.had_hint
        )
        
        return {
            "success": True,
            "concept_id": record.concept_id,
            "current_level": record.current_level,
            "is_mastered": record.is_mastered,
            "streak_current": record.streak_current,
            "next_review_due": record.next_review_due.isoformat() if record.next_review_due else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mastery/summary/{test_id}")
async def get_mastery_summary(
    test_id: str,
    db: Session = Depends(get_db)
):
    """Get overall mastery summary for a student."""
    try:
        test_uuid = uuid.UUID(test_id)
        summary = MasteryService.get_mastery_summary(db, test_uuid)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mastery/due-for-review/{test_id}")
async def get_concepts_due_for_review(
    test_id: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get concepts that are due for review (spaced repetition)."""
    try:
        test_uuid = uuid.UUID(test_id)
        records = MasteryService.get_concepts_due_for_review(db, test_uuid, limit)
        
        return {
            "concepts_due": [
                {
                    "concept_id": r.concept_id,
                    "current_level": r.current_level,
                    "last_practiced": r.last_practiced.isoformat() if r.last_practiced else None,
                    "next_review_due": r.next_review_due.isoformat() if r.next_review_due else None,
                    "questions_to_review": 3  # Default
                }
                for r in records
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== DIAGNOSTIC ENDPOINTS =====

@router.post("/diagnostic/create")
async def create_diagnostic_test(
    request: DiagnosticRequest,
    db: Session = Depends(get_db)
):
    """Create an adaptive diagnostic test."""
    try:
        service = DiagnosticService()
        result = await service.create_diagnostic_test(
            db=db,
            grade_level=request.grade_level,
            subject=request.subject,
            exam_standard=request.exam_standard
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagnostic/analyze")
async def analyze_diagnostic_results(
    test_id: str,
    answers: dict,
    db: Session = Depends(get_db)
):
    """Analyze diagnostic test results and create learning profile."""
    try:
        from app.models.test import Question
        
        test_uuid = uuid.UUID(test_id)
        
        # Get questions for this test
        questions = db.query(Question).filter(Question.test_id == test_uuid).all()
        
        service = DiagnosticService()
        results = service.analyze_diagnostic_results(
            db=db,
            test_id=test_uuid,
            answers=answers,
            questions=questions
        )
        
        # Create personalized learning path
        learning_path = service.create_personalized_learning_path(
            db=db,
            diagnostic_results=results,
            grade_level=questions[0].test.grade_level if questions else 5
        )
        
        return {
            "diagnostic_results": results,
            "learning_path": learning_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== ADAPTIVE DIFFICULTY ENDPOINTS =====

@router.get("/adaptive/difficulty/{test_id}/{concept_id}")
async def get_current_difficulty(
    test_id: str,
    concept_id: str,
    db: Session = Depends(get_db)
):
    """Get the current appropriate difficulty level for a student."""
    try:
        test_uuid = uuid.UUID(test_id)
        difficulty = AdaptiveDifficultyService.calculate_current_difficulty(
            db=db,
            test_id=test_uuid,
            concept_id=concept_id
        )
        
        return {
            "concept_id": concept_id,
            "difficulty_score": difficulty,
            "difficulty_label": AdaptiveDifficultyService.get_difficulty_label(difficulty).value
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adaptive/practice-session")
async def generate_practice_session(
    request: PracticeSessionRequest,
    db: Session = Depends(get_db)
):
    """Generate a personalized practice session."""
    try:
        test_uuid = uuid.UUID(request.test_id)
        
        queue = PersonalizedPracticeQueue.generate_practice_session(
            db=db,
            test_id=test_uuid,
            target_questions=request.target_questions,
            mix_ratio=request.mix_ratio
        )
        
        return {
            "practice_queue": queue,
            "total_questions": len(queue)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== LEARNING ANALYTICS =====

@router.get("/analytics/progress/{test_id}")
async def get_learning_progress(
    test_id: str,
    db: Session = Depends(get_db)
):
    """Get comprehensive learning progress analytics."""
    try:
        test_uuid = uuid.UUID(test_id)
        
        # Get mastery summary
        mastery_summary = MasteryService.get_mastery_summary(db, test_uuid)
        
        # Get concepts due for review
        due_concepts = MasteryService.get_concepts_due_for_review(db, test_uuid, limit=100)
        
        return {
            "mastery_summary": mastery_summary,
            "concepts_due_count": len(due_concepts),
            "learning_streak": mastery_summary.get("best_streak", 0),
            "overall_mastery": mastery_summary.get("overall_mastery", 0.0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

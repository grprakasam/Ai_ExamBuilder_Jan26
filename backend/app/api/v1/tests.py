from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api import deps
from app.db.session import get_db
from app.schemas.test import TestCreate, TestWithQuestions
from app.services.question_generator import QuestionGenerator
from app.models.test import Test, Question, QuestionTypeEnum
import uuid

router = APIRouter()

@router.post("/generate", response_model=TestWithQuestions)
async def generate_test(
    *,
    db: Session = Depends(get_db),
    test_in: TestCreate
):
    """
    Generate a new practice test using AI.
    """
    generator = QuestionGenerator()

    try:
        # 1. Generate questions using AI
        questions_data = await generator.generate_questions(
            grade=test_in.grade_level,
            subject=test_in.subject.value,
            standard=test_in.standard_focus,
            count=test_in.question_count,
            q_type=test_in.question_type.value,
            difficulty=test_in.difficulty.value
        )

        # 2. Create the test record
        db_test = Test(
            title=test_in.title,
            grade_level=test_in.grade_level,
            subject=test_in.subject,
            standard_focus=test_in.standard_focus,
            question_count=test_in.question_count,
            question_type=test_in.question_type,
            difficulty=test_in.difficulty,
            # created_by=current_user.id  # Add after auth implementation
        )
        db.add(db_test)
        db.flush() # Get the test ID

        # 3. Create question records
        for q_data in questions_data:
            db_question = Question(
                test_id=db_test.id,
                sequence=q_data.get("sequence"),
                question_text=q_data.get("question_text"),
                question_type=test_in.question_type,
                options=q_data.get("options"),
                correct_answer=q_data.get("correct_answer"),
                explanation=q_data.get("explanation"),
                cognitive_level=q_data.get("cognitive_level")
            )
            db.add(db_question)

        db.commit()
        db.refresh(db_test)
        return db_test

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate test: {str(e)}"
        )

@router.get("/list/recent", response_model=List[TestWithQuestions])
@router.get("/recent", response_model=List[TestWithQuestions])
def get_recent_tests(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get a list of recent tests.
    """
    return db.query(Test).order_by(Test.created_at.desc()).limit(limit).all()

@router.get("/{test_id}", response_model=TestWithQuestions)
def get_test(test_id: uuid.UUID, db: Session = Depends(get_db)):
    db_test = db.query(Test).filter(Test.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    return db_test

from app.services.feedback_engine import FeedbackEngine

@router.post("/{test_id}/submit")
async def submit_test(
    test_id: uuid.UUID,
    answers: dict,
    db: Session = Depends(get_db)
):
    """
    Submit test answers and calculate score with AI feedback.
    """
    db_test = db.query(Test).filter(Test.id == test_id).first()
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
        
    engine = FeedbackEngine()
    
    # Prepare questions for the engine
    test_data = []
    for q in db_test.questions:
        test_data.append({
            "question_text": q.question_text,
            "correct_answer": q.correct_answer,
            "question_type": q.question_type
        })
        
    feedback_result = await engine.evaluate_responses(test_data, answers)
    
    # Calculate simple score for MCQ if any
    correct_count = 0
    total_mcq = 0
    for i, q in enumerate(db_test.questions):
        if q.question_type == QuestionTypeEnum.MCQ:
            total_mcq += 1
            user_ans = answers.get(str(i))
            if user_ans == q.correct_answer:
                correct_count += 1
                
    mcq_score = (correct_count / total_mcq) * 100 if total_mcq > 0 else None
    
    return {
        "score": mcq_score,
        "correct_count": correct_count,
        "total_mcq": total_mcq,
        "ai_feedback": feedback_result
    }

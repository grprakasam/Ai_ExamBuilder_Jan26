import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api import deps
from app.db.session import get_db
from app.schemas.test import TestCreate, TestWithQuestions, TestResponse
from app.schemas.generated import GeneratedQuestions
from app.models.test import Test, Question
from app.models.concept import Concept
from app.services.question_generator import QuestionGenerator
from app.services.feedback_engine import FeedbackEngine
from app.services.access_code_service import AccessCodeService
from app.services.mastery_service import MasteryService
from app.services.adaptive_difficulty import PersonalizedPracticeQueue
from app.services.exam_profiles import PROFILES
from app.services.scoring import score_questions

router = APIRouter()
log = logging.getLogger(__name__)

class Submission(BaseModel):
    attempt_id: uuid.UUID
    answers: dict[str, str]
    time_taken_seconds: int = Field(0, ge=0)
    include_feedback: bool = True

class PracticeAnswer(BaseModel):
    attempt_id: uuid.UUID
    question_index: int = Field(ge=0)
    answer: str
    time_taken_seconds: float = Field(0, ge=0)
    had_hint: bool = False

@router.get("/exam-profiles")
def exam_profiles():
    return {key: {"name": name, "topics": topics} for key, (name, topics) in PROFILES.items()}

@router.post("/generate", response_model=TestWithQuestions)
async def generate_test(test_in: TestCreate, db: Session = Depends(get_db)):
    try:
        data = await QuestionGenerator().generate_questions(
            grade=test_in.grade_level, subject=test_in.subject.value,
            standard=test_in.standard_focus, count=test_in.question_count,
            q_type=test_in.question_type.value, difficulty=test_in.difficulty.value,
            exam_standard=test_in.exam_standard.value)
        validated = GeneratedQuestions.model_validate({"questions": data})
        if len(validated.questions) != test_in.question_count:
            raise ValueError("Model returned the wrong number of questions")
        if test_in.question_type.value != "mixed" and any(
            q.question_type != test_in.question_type for q in validated.questions
        ):
            raise ValueError("Model returned the wrong question type")
        code = AccessCodeService.generate_access_code()
        while db.query(Test).filter(Test.access_code == code).first():
            code = AccessCodeService.generate_access_code()
        test = Test(**test_in.model_dump(), access_code=code)
        db.add(test)
        db.flush()
        for q in validated.questions:
            values = q.model_dump(exclude={"times_attempted", "times_correct", "avg_time_seconds"})
            db.add(Question(test_id=test.id, **values))
            for cid in q.concept_ids or []:
                if not db.query(Concept).filter(Concept.concept_id == cid).first():
                    db.add(Concept(concept_id=cid, name=cid, subject=test_in.subject.value,
                                   exam_standard=test_in.exam_standard.value,
                                   grade_level_min=test_in.grade_level, grade_level_max=test_in.grade_level))
                    db.flush()
        db.commit()
        db.refresh(test)
        return test
    except ValueError as exc:
        db.rollback()
        raise HTTPException(502, f"Generated questions failed validation: {exc}")
    except Exception:
        db.rollback()
        log.exception("Question generation failed")
        raise HTTPException(502, "Question generation unavailable")

@router.get("/list/recent", response_model=list[TestResponse])
@router.get("/recent", response_model=list[TestResponse])
def recent_tests(db: Session = Depends(get_db), limit: int = 10):
    return db.query(Test).order_by(Test.created_at.desc()).limit(min(max(limit, 1), 50)).all()

@router.get("/{test_id}", response_model=TestWithQuestions, response_model_exclude={"access_code"})
def get_test(test: Test = Depends(deps.require_test_access)):
    return test

def update_learning(db, test, question, answer, seconds, had_hint, learner_key):
    if question.question_type.value != "mcq":
        return  # Written-response correctness requires human review, not string matching.
    for cid in question.concept_ids or []:
        MasteryService.update_mastery_record(db, test.id, cid, answer == question.correct_answer,
                                            seconds, had_hint, learner_key=learner_key, commit=False)

@router.post("/{test_id}/practice-answer")
def practice_answer(test_id: uuid.UUID, body: PracticeAnswer, request: Request,
                    test: Test = Depends(deps.require_test_access), db: Session = Depends(get_db)):
    attempt = deps.authorize_attempt(db, test_id, body.attempt_id, request)
    if body.question_index >= len(test.questions):
        raise HTTPException(422, "Question index out of range")
    key = str(body.question_index)
    if key in (attempt.answers or {}):
        raise HTTPException(409, "This question has already been recorded")
    q = test.questions[body.question_index]
    try:
        score_questions([q], {"0": body.answer}, test.exam_standard)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    update_learning(db, test, q, body.answer, body.time_taken_seconds, body.had_hint, attempt.session_hash)
    attempt.answers = {**(attempt.answers or {}), key: body.answer}
    db.commit()
    recent = [
        {"concept_id": (test.questions[int(index)].concept_ids or [None])[0],
         "difficulty_score": test.questions[int(index)].difficulty_score or 0.5,
         "is_correct": answer == test.questions[int(index)].correct_answer}
        for index, answer in attempt.answers.items()
        if test.questions[int(index)].question_type.value == "mcq"
    ]
    rec = PersonalizedPracticeQueue.get_next_question_recommendation(
        db, test.id, recent, learner_key=attempt.session_hash)
    candidates = [(i, candidate) for i, candidate in enumerate(test.questions) if str(i) not in attempt.answers]
    target = rec.get("difficulty_score", 0.5)
    next_index = min(candidates, key=lambda item: abs((item[1].difficulty_score or 0.5) - target))[0] if candidates else None
    return {"is_correct": body.answer == q.correct_answer if q.question_type.value == "mcq" else None, "next_question_index": next_index,
            "recommendation": rec}

@router.post("/{test_id}/submit")
async def submit_test(test_id: uuid.UUID, body: Submission, request: Request,
                      test: Test = Depends(deps.require_test_access), db: Session = Depends(get_db)):
    attempt = deps.authorize_attempt(db, test_id, body.attempt_id, request)
    if any(not key.isdigit() or int(key) >= len(test.questions) for key in body.answers):
        raise HTTPException(422, "Unknown question index")
    if any(body.answers.get(key) != value for key, value in (attempt.answers or {}).items()):
        raise HTTPException(409, "Recorded practice answers cannot be changed")
    try:
        result = score_questions(test.questions, body.answers, test.exam_standard)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    for i, q in enumerate(test.questions):
        key = str(i)
        if key in body.answers and key not in (attempt.answers or {}):
            update_learning(db, test, q, body.answers[key],
                            body.time_taken_seconds / max(len(test.questions), 1), False, attempt.session_hash)
    attempt = AccessCodeService.complete_exam_attempt(
        db, body.attempt_id, body.answers, result["score"], body.time_taken_seconds, test.passing_score * 100)
    feedback = None
    if body.include_feedback:
        try:
            questions = [{"question_text": q.question_text, "correct_answer": q.correct_answer,
                          "question_type": q.question_type.value, "exam_standard": test.exam_standard.value}
                         for q in test.questions]
            feedback = await FeedbackEngine().evaluate_responses(questions, body.answers)
        except Exception:
            log.warning("Optional model feedback unavailable")
    return {**result, "attempt_id": str(attempt.id), "ai_feedback": feedback,
            "feedback_available": feedback is not None}

@router.get("/{test_id}/results/{attempt_id}")
def saved_results(test_id: uuid.UUID, attempt_id: uuid.UUID, request: Request,
                  test: Test = Depends(deps.require_test_access), db: Session = Depends(get_db)):
    from app.models.exam_attempt import ExamAttempt
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id, ExamAttempt.test_id == test_id,
                                          ExamAttempt.session_hash == deps.session_hash(request)).first()
    if not attempt or not attempt.is_completed:
        raise HTTPException(404, "Completed attempt not found")
    return {**score_questions(test.questions, attempt.answers or {}, test.exam_standard),
            "answers": attempt.answers, "attempt_id": str(attempt.id)}

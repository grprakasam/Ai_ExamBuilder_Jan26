from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.models.test import SubjectEnum, QuestionTypeEnum, DifficultyEnum, BloomLevelEnum, LearningModeEnum, ExamStandardEnum
from uuid import UUID
from datetime import datetime

class QuestionBase(BaseModel):
    sequence: int
    question_text: str
    question_type: QuestionTypeEnum
    options: Optional[Dict[str, str]] = None
    correct_answer: str
    
    # Legacy fields (backward compatibility)
    explanation: Optional[str] = None
    cognitive_level: Optional[str] = None
    
    # Learning-Centered Fields
    concept_ids: Optional[List[str]] = None
    prerequisite_concepts: Optional[List[str]] = None
    learning_objective: Optional[str] = None
    bloom_level: Optional[BloomLevelEnum] = None
    difficulty_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Rich Feedback
    explanation_correct: Optional[str] = None
    explanation_wrong: Optional[Dict[str, str]] = None  # {"A": "why wrong", "B": "why wrong"}
    common_misconceptions: Optional[List[str]] = None
    worked_example: Optional[str] = None
    hint: Optional[str] = None
    
    # Analytics (read-only, populated by system)
    times_attempted: Optional[int] = 0
    times_correct: Optional[int] = 0
    avg_time_seconds: Optional[float] = None

class TestBase(BaseModel):
    title: str
    grade_level: int = Field(..., ge=3, le=12)
    subject: SubjectEnum
    standard_focus: str
    question_count: int = Field(..., ge=1, le=50)
    question_type: QuestionTypeEnum
    difficulty: DifficultyEnum
    exam_standard: Optional[ExamStandardEnum] = ExamStandardEnum.NCDPI

class TestCreate(TestBase):
    pass

class TestResponse(TestBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class TestWithQuestions(TestResponse):
    questions: List[QuestionBase]

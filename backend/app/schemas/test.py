from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.models.test import SubjectEnum, QuestionTypeEnum, DifficultyEnum
from uuid import UUID
from datetime import datetime

class QuestionBase(BaseModel):
    sequence: int
    question_text: str
    question_type: QuestionTypeEnum
    options: Optional[Dict[str, str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    cognitive_level: Optional[str] = None

class TestBase(BaseModel):
    title: str
    grade_level: int = Field(..., ge=3, le=12)
    subject: SubjectEnum
    standard_focus: str
    question_count: int = Field(..., ge=1, le=50)
    question_type: QuestionTypeEnum
    difficulty: DifficultyEnum

class TestCreate(TestBase):
    pass

class TestResponse(TestBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class TestWithQuestions(TestResponse):
    questions: List[QuestionBase]

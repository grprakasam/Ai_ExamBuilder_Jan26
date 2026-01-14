from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean, Text, Enum, TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_class import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import enum

# Custom UUID type that works with both SQLite and PostgreSQL
class UUID(TypeDecorator):
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, str):
                return uuid.UUID(value)
            return value

class SubjectEnum(str, enum.Enum):
    MATH = "mathematics"
    ENGLISH = "english"
    SCIENCE = "science"
    SOCIAL_STUDIES = "social_studies"

class QuestionTypeEnum(str, enum.Enum):
    MCQ = "mcq"
    OPEN_ENDED = "open_ended"

class DifficultyEnum(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Test(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    created_by = Column(UUID, ForeignKey("user.id"), nullable=True)
    title = Column(String)
    grade_level = Column(Integer)
    subject = Column(Enum(SubjectEnum))
    standard_focus = Column(String)
    question_count = Column(Integer)
    question_type = Column(Enum(QuestionTypeEnum))
    difficulty = Column(Enum(DifficultyEnum))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_published = Column(Boolean, default=True)
    
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")

class Question(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID, ForeignKey("test.id"))
    sequence = Column(Integer)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionTypeEnum))
    options = Column(JSON)  # For MCQ: {"A": "...", "B": "...", ...}
    correct_answer = Column(String)
    explanation = Column(Text)
    cognitive_level = Column(String)
    
    test = relationship("Test", back_populates="questions")

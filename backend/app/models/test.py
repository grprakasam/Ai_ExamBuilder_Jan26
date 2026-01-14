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
    MIXED = "mixed"  # Mix of MCQ and open-ended

class DifficultyEnum(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class BloomLevelEnum(str, enum.Enum):
    """Bloom's Taxonomy cognitive levels"""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class LearningModeEnum(str, enum.Enum):
    """Three learning modes for different purposes"""
    LEARN = "learn"        # Immediate feedback, hints available, unlimited retries
    PRACTICE = "practice"  # Immediate feedback, no hints, retry wrong questions
    ASSESSMENT = "assessment"  # Timed, no feedback until end

class ExamStandardEnum(str, enum.Enum):
    """Supported exam standards for global coverage"""
    NCDPI = "ncdpi"        # North Carolina (US)
    NEET = "neet"          # Medical entrance (India)
    JEE = "jee"            # Engineering entrance (India)
    CBSE = "cbse"          # Central Board (India)
    ICSE = "icse"          # Indian Certificate (India)
    TN_GOVT = "tn_govt"    # Tamil Nadu Government (India)
    SAT = "sat"            # Standardized test (US)
    ACT = "act"            # Standardized test (US)

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
    
    # ===== AUTHENTICATION & ACCESS CONTROL (PII-minimal) =====
    access_code = Column(String(8), unique=True, index=True)  # 8-character alphanumeric code
    max_attempts = Column(Integer, default=3)  # Maximum number of attempts allowed
    code_expiration = Column(DateTime, nullable=True)  # Optional expiration date
    is_active = Column(Boolean, default=True)  # Can be deactivated by admin
    
    # ===== MULTI-EXAM STANDARD SUPPORT =====
    exam_standard = Column(Enum(ExamStandardEnum), default=ExamStandardEnum.NCDPI)
    
    # ===== TEST CONFIGURATION =====
    time_limit_minutes = Column(Integer, nullable=True)  # Optional time limit
    passing_score = Column(Float, default=0.6)  # 60% default
    shuffle_questions = Column(Boolean, default=False)
    shuffle_options = Column(Boolean, default=False)
    
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")

class Question(Base):
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    test_id = Column(UUID, ForeignKey("test.id"))
    sequence = Column(Integer)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionTypeEnum))
    options = Column(JSON)  # For MCQ: {"A": "...", "B": "...", ...}
    correct_answer = Column(String)
    
    # Legacy field - keeping for backward compatibility
    explanation = Column(Text)
    cognitive_level = Column(String)
    
    # ===== LEARNING-CENTERED FIELDS =====
    
    # Concept Mapping
    concept_ids = Column(JSON)  # ["fractions", "decimals", "place-value"]
    prerequisite_concepts = Column(JSON)  # Concepts student must know first
    learning_objective = Column(Text)  # What this question teaches
    
    # Cognitive Taxonomy
    bloom_level = Column(Enum(BloomLevelEnum))  # Bloom's taxonomy level
    difficulty_score = Column(Float)  # 0.0-1.0 precise difficulty (more granular than easy/medium/hard)
    
    # Rich Feedback for Learning
    explanation_correct = Column(Text)  # Why the correct answer is correct
    explanation_wrong = Column(JSON)  # {"A": "why A is wrong", "B": "why B is wrong", ...}
    common_misconceptions = Column(JSON)  # ["Students often confuse X with Y", ...]
    worked_example = Column(Text)  # Step-by-step solution
    hint = Column(Text)  # Scaffolded hint without giving away answer
    
    # Learning Analytics (populated over time)
    times_attempted = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    avg_time_seconds = Column(Float)  # Average time students take
    
    test = relationship("Test", back_populates="questions")

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean, Text, TypeDecorator
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_class import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

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


class Concept(Base):
    """
    Represents a learning concept with hierarchical relationships.
    Examples: "fractions.adding", "algebra.linear-equations", "geometry.triangles"
    """
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    concept_id = Column(String, unique=True, nullable=False, index=True)  # e.g., "fractions.adding"
    name = Column(String, nullable=False)  # e.g., "Adding Fractions"
    description = Column(Text)
    
    # Hierarchy
    parent_concept_id = Column(String, ForeignKey("concept.concept_id"), nullable=True)
    
    # Metadata
    subject = Column(String)  # mathematics, science, etc.
    grade_level_min = Column(Integer)  # Minimum grade level
    grade_level_max = Column(Integer)  # Maximum grade level
    exam_standard = Column(String)  # NCDPI, NEET, CBSE, etc.
    
    # Prerequisites (JSON array of concept_ids)
    prerequisite_concept_ids = Column(JSON)  # ["fractions.basics", "multiplication"]
    
    # Learning Resources
    learning_resources = Column(JSON)  # URLs, video links, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("Concept", remote_side=[concept_id], backref="children")


class MasteryRecord(Base):
    """
    Tracks a student's mastery of a specific concept.
    Uses spaced repetition (SM-2 algorithm) for optimal review scheduling.
    """
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    
    # Links to test access (not user, to maintain PII-minimal design)
    test_id = Column(UUID, ForeignKey("test.id"))
    concept_id = Column(String, ForeignKey("concept.concept_id"), nullable=False)
    
    # Mastery Metrics
    current_level = Column(Float, default=0.0)  # 0.0 to 1.0 (0-100%)
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    
    # Streaks
    streak_current = Column(Integer, default=0)  # Consecutive correct answers
    streak_best = Column(Integer, default=0)  # Best streak achieved
    
    # Spaced Repetition (SM-2 Algorithm)
    last_practiced = Column(DateTime)
    next_review_due = Column(DateTime)
    ease_factor = Column(Float, default=2.5)  # SM-2 ease factor (1.3 to 2.5+)
    interval_days = Column(Integer, default=1)  # Days until next review
    repetitions = Column(Integer, default=0)  # Number of successful repetitions
    
    # Learning Velocity
    avg_time_to_correct = Column(Float)  # Average seconds to answer correctly
    improvement_rate = Column(Float)  # Rate of improvement over time
    first_attempt_date = Column(DateTime, server_default=func.now())
    mastery_achieved_date = Column(DateTime)  # When mastery (>80%) was first achieved
    
    # Status
    is_mastered = Column(Boolean, default=False)  # True when current_level >= 0.8
    needs_review = Column(Boolean, default=False)  # True when next_review_due has passed
    
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    test = relationship("Test")
    concept = relationship("Concept")

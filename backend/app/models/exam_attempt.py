from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Float, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base_class import Base
from app.models.test import UUID
import uuid


class ExamAttempt(Base):
    """
    Tracks individual exam attempts for PII-minimal access control.
    Links TEST_ID + ACCESS_CODE without requiring user accounts.
    """
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    
    # Test identification
    test_id = Column(UUID, ForeignKey("test.id"), nullable=False)
    access_code = Column(String(8), nullable=False)  # Code used for this attempt
    
    # Attempt tracking
    attempt_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Session identification (no PII)
    session_hash = Column(String, index=True)  # Hashed IP + User Agent for basic tracking
    
    # Results
    answers = Column(JSON)  # {question_index: answer}
    score = Column(Float, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_passed = Column(Boolean, nullable=True)
    
    # Relationships
    test = relationship("Test")


class AttemptRequest(Base):
    """
    Tracks requests for additional attempts beyond the default limit.
    Requires admin approval.
    """
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    
    # Test identification
    test_id = Column(UUID, ForeignKey("test.id"), nullable=False)
    access_code = Column(String(8), nullable=False)
    
    # Request details
    current_attempts = Column(Integer, nullable=False)
    requested_attempts = Column(Integer, nullable=False)
    reason = Column(Text, nullable=True)  # Optional reason from student
    
    # Admin review
    status = Column(String, default="pending")  # pending, approved, rejected
    reviewed_by = Column(UUID, ForeignKey("user.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    test = relationship("Test")

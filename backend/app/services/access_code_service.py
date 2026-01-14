import secrets
import string
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.test import Test
from app.models.exam_attempt import ExamAttempt, AttemptRequest
import uuid


class AccessCodeService:
    """
    Service for managing TEST_ID + ACCESS_CODE authentication.
    PII-minimal design - no user accounts required.
    """
    
    # Access code configuration
    CODE_LENGTH = 8
    CODE_CHARS = string.ascii_uppercase + string.digits  # A-Z, 0-9
    
    @staticmethod
    def generate_access_code() -> str:
        """
        Generate a unique 8-character alphanumeric access code.
        Format: XXXX-XXXX for readability (but stored without hyphen)
        """
        code = ''.join(secrets.choice(AccessCodeService.CODE_CHARS) 
                      for _ in range(AccessCodeService.CODE_LENGTH))
        return code
    
    @staticmethod
    def format_code_display(code: str) -> str:
        """Format code for display: ABCD1234 -> ABCD-1234"""
        if len(code) == 8:
            return f"{code[:4]}-{code[4:]}"
        return code
    
    @staticmethod
    def create_session_hash(ip_address: str, user_agent: str) -> str:
        """
        Create a hash of IP + User Agent for basic session tracking.
        No PII stored - just a hash for attempt limiting.
        """
        session_string = f"{ip_address}:{user_agent}"
        return hashlib.sha256(session_string.encode()).hexdigest()
    
    @staticmethod
    def validate_access_code(
        db: Session,
        test_id: uuid.UUID,
        access_code: str,
        session_hash: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate access code and check attempt limits.
        
        Returns:
            (is_valid, error_message)
        """
        # Get test
        test = db.query(Test).filter(Test.id == test_id).first()
        if not test:
            return False, "Test not found"
        
        # Check if test is active
        if not test.is_active:
            return False, "This test is no longer active"
        
        # Verify access code
        if test.access_code != access_code.replace("-", "").upper():
            return False, "Invalid access code"
        
        # Check expiration
        if test.code_expiration and test.code_expiration < datetime.now():
            return False, "Access code has expired"
        
        # Count attempts for this session
        attempts = db.query(ExamAttempt).filter(
            ExamAttempt.test_id == test_id,
            ExamAttempt.session_hash == session_hash
        ).count()
        
        if attempts >= test.max_attempts:
            return False, f"Maximum attempts ({test.max_attempts}) reached. Request additional attempts if needed."
        
        return True, None
    
    @staticmethod
    def start_exam_attempt(
        db: Session,
        test_id: uuid.UUID,
        access_code: str,
        session_hash: str
    ) -> Optional[ExamAttempt]:
        """
        Start a new exam attempt.
        
        Returns:
            ExamAttempt object or None if validation fails
        """
        # Validate access
        is_valid, error = AccessCodeService.validate_access_code(
            db, test_id, access_code, session_hash
        )
        
        if not is_valid:
            return None
        
        # Count existing attempts
        attempt_number = db.query(ExamAttempt).filter(
            ExamAttempt.test_id == test_id,
            ExamAttempt.session_hash == session_hash
        ).count() + 1
        
        # Create new attempt
        attempt = ExamAttempt(
            test_id=test_id,
            access_code=access_code,
            attempt_number=attempt_number,
            session_hash=session_hash,
            answers={}
        )
        
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
        
        return attempt
    
    @staticmethod
    def complete_exam_attempt(
        db: Session,
        attempt_id: uuid.UUID,
        answers: dict,
        score: float,
        time_taken_seconds: int,
        passing_score: float = 0.6
    ) -> ExamAttempt:
        """
        Complete an exam attempt with results.
        """
        attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
        
        if not attempt:
            raise ValueError("Attempt not found")
        
        attempt.answers = answers
        attempt.score = score
        attempt.time_taken_seconds = time_taken_seconds
        attempt.is_completed = True
        attempt.is_passed = score >= passing_score
        attempt.completed_at = datetime.now()
        
        db.commit()
        db.refresh(attempt)
        
        return attempt
    
    @staticmethod
    def request_additional_attempts(
        db: Session,
        test_id: uuid.UUID,
        access_code: str,
        session_hash: str,
        requested_attempts: int,
        reason: Optional[str] = None
    ) -> AttemptRequest:
        """
        Submit a request for additional attempts.
        Requires admin approval.
        """
        # Count current attempts
        current_attempts = db.query(ExamAttempt).filter(
            ExamAttempt.test_id == test_id,
            ExamAttempt.session_hash == session_hash
        ).count()
        
        # Create request
        request = AttemptRequest(
            test_id=test_id,
            access_code=access_code,
            current_attempts=current_attempts,
            requested_attempts=requested_attempts,
            reason=reason,
            status="pending"
        )
        
        db.add(request)
        db.commit()
        db.refresh(request)
        
        return request
    
    @staticmethod
    def get_attempt_summary(
        db: Session,
        test_id: uuid.UUID,
        session_hash: str
    ) -> dict:
        """
        Get summary of attempts for a session.
        """
        test = db.query(Test).filter(Test.id == test_id).first()
        attempts = db.query(ExamAttempt).filter(
            ExamAttempt.test_id == test_id,
            ExamAttempt.session_hash == session_hash
        ).all()
        
        completed_attempts = [a for a in attempts if a.is_completed]
        best_score = max((a.score for a in completed_attempts), default=0.0)
        
        return {
            "test_id": str(test_id),
            "test_title": test.title if test else "Unknown",
            "attempts_used": len(attempts),
            "max_attempts": test.max_attempts if test else 0,
            "attempts_remaining": max(0, (test.max_attempts if test else 0) - len(attempts)),
            "best_score": best_score,
            "passed": best_score >= (test.passing_score if test else 0.6),
            "attempts": [
                {
                    "attempt_number": a.attempt_number,
                    "score": a.score,
                    "is_passed": a.is_passed,
                    "time_taken_seconds": a.time_taken_seconds,
                    "completed_at": a.completed_at.isoformat() if a.completed_at else None
                }
                for a in completed_attempts
            ]
        }

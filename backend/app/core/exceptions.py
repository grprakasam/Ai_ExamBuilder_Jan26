"""
Custom exceptions for the EduApp platform.
Provides granular error handling with proper HTTP status codes.
"""
from fastapi import HTTPException, status


# ===== BASE EXCEPTIONS =====

class EduAppException(Exception):
    """Base exception for all EduApp errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# ===== AUTHENTICATION & ACCESS CONTROL =====

class InvalidAccessCodeError(EduAppException):
    """Raised when access code is invalid or expired."""
    def __init__(self, message: str = "Invalid or expired access code"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class AttemptLimitExceededError(EduAppException):
    """Raised when maximum attempts have been reached."""
    def __init__(self, max_attempts: int):
        super().__init__(
            f"Maximum attempts ({max_attempts}) reached. Request additional attempts if needed.",
            status.HTTP_403_FORBIDDEN
        )


class TestNotActiveError(EduAppException):
    """Raised when trying to access an inactive test."""
    def __init__(self):
        super().__init__("This test is no longer active", status.HTTP_403_FORBIDDEN)


# ===== RESOURCE NOT FOUND =====

class TestNotFoundError(EduAppException):
    """Raised when test is not found."""
    def __init__(self, test_id: str):
        super().__init__(f"Test {test_id} not found", status.HTTP_404_NOT_FOUND)


class QuestionNotFoundError(EduAppException):
    """Raised when question is not found."""
    def __init__(self, question_id: str):
        super().__init__(f"Question {question_id} not found", status.HTTP_404_NOT_FOUND)


class ConceptNotFoundError(EduAppException):
    """Raised when concept is not found."""
    def __init__(self, concept_id: str):
        super().__init__(f"Concept {concept_id} not found", status.HTTP_404_NOT_FOUND)


class AttemptNotFoundError(EduAppException):
    """Raised when exam attempt is not found."""
    def __init__(self, attempt_id: str):
        super().__init__(f"Attempt {attempt_id} not found", status.HTTP_404_NOT_FOUND)


# ===== VALIDATION ERRORS =====

class InvalidGradeLevelError(EduAppException):
    """Raised when grade level is out of valid range."""
    def __init__(self, grade: int):
        super().__init__(
            f"Invalid grade level: {grade}. Must be between 1 and 12.",
            status.HTTP_400_BAD_REQUEST
        )


class InvalidDifficultyScoreError(EduAppException):
    """Raised when difficulty score is out of range."""
    def __init__(self, score: float):
        super().__init__(
            f"Invalid difficulty score: {score}. Must be between 0.0 and 1.0.",
            status.HTTP_400_BAD_REQUEST
        )


class InvalidMasteryLevelError(EduAppException):
    """Raised when mastery level is out of range."""
    def __init__(self, level: float):
        super().__init__(
            f"Invalid mastery level: {level}. Must be between 0.0 and 1.0.",
            status.HTTP_400_BAD_REQUEST
        )


class MissingRequiredFieldError(EduAppException):
    """Raised when required field is missing."""
    def __init__(self, field_name: str):
        super().__init__(
            f"Required field missing: {field_name}",
            status.HTTP_400_BAD_REQUEST
        )


# ===== LEARNING SERVICE ERRORS =====

class PrerequisiteNotMetError(EduAppException):
    """Raised when attempting to learn a concept without mastering prerequisites."""
    def __init__(self, concept_id: str, prerequisites: list):
        prereq_str = ", ".join(prerequisites)
        super().__init__(
            f"Cannot start {concept_id}. Must master prerequisites first: {prereq_str}",
            status.HTTP_400_BAD_REQUEST
        )


class DiagnosticNotCompletedError(EduAppException):
    """Raised when trying to access features that require diagnostic completion."""
    def __init__(self):
        super().__init__(
            "Please complete the diagnostic assessment first",
            status.HTTP_400_BAD_REQUEST
        )


class InsufficientQuestionsError(EduAppException):
    """Raised when not enough questions available for requested operation."""
    def __init__(self, requested: int, available: int):
        super().__init__(
            f"Requested {requested} questions but only {available} available",
            status.HTTP_400_BAD_REQUEST
        )


# ===== AI SERVICE ERRORS =====

class AIGenerationError(EduAppException):
    """Raised when AI question generation fails."""
    def __init__(self, reason: str = "AI generation failed"):
        super().__init__(
            f"Failed to generate questions: {reason}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class InvalidAIResponseError(EduAppException):
    """Raised when AI returns invalid or incomplete response."""
    def __init__(self, details: str = ""):
        super().__init__(
            f"AI returned invalid response. {details}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===== DATABASE ERRORS =====

class DatabaseError(EduAppException):
    """Raised for database operation failures."""
    def __init__(self, operation: str, details: str = ""):
        super().__init__(
            f"Database {operation} failed. {details}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class DuplicateRecordError(EduAppException):
    """Raised when trying to create duplicate record."""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} with identifier {identifier} already exists",
            status.HTTP_409_CONFLICT
        )


# ===== RATE LIMITING =====

class RateLimitExceededError(EduAppException):
    """Raised when rate limit is exceeded."""
    def __init__(self, retry_after: int):
        super().__init__(
            f"Rate limit exceeded. Try again in {retry_after} seconds.",
            status.HTTP_429_TOO_MANY_REQUESTS
        )


# ===== HELPER FUNCTIONS =====

def handle_exception(exc: Exception) -> HTTPException:
    """
    Convert custom exceptions to FastAPI HTTPException.
    
    Args:
        exc: The exception to convert
        
    Returns:
        HTTPException with appropriate status code and message
    """
    if isinstance(exc, EduAppException):
        return HTTPException(
            status_code=exc.status_code,
            detail=exc.message
        )
    
    # Generic error for unexpected exceptions
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred. Please try again later."
    )

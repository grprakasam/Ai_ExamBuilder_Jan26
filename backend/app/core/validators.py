"""
Input validation utilities for the EduApp platform.
Provides comprehensive validation with detailed error messages.
"""
from typing import List, Optional, Dict, Any
from app.core.exceptions import (
    InvalidGradeLevelError,
    InvalidDifficultyScoreError,
    InvalidMasteryLevelError,
    MissingRequiredFieldError
)
import re


class Validators:
    """Collection of validation methods for common inputs."""
    
    # Constants
    MIN_GRADE = 1
    MAX_GRADE = 12
    MIN_DIFFICULTY = 0.0
    MAX_DIFFICULTY = 1.0
    MIN_MASTERY = 0.0
    MAX_MASTERY = 1.0
    ACCESS_CODE_PATTERN = r'^[A-Z0-9]{8}$'
    
    @staticmethod
    def validate_grade_level(grade: int) -> int:
        """
        Validate grade level is within acceptable range.
        
        Args:
            grade: Grade level to validate
            
        Returns:
            Validated grade level
            
        Raises:
            InvalidGradeLevelError: If grade is out of range
        """
        if not isinstance(grade, int):
            raise InvalidGradeLevelError(grade)
        
        if grade < Validators.MIN_GRADE or grade > Validators.MAX_GRADE:
            raise InvalidGradeLevelError(grade)
        
        return grade
    
    @staticmethod
    def validate_difficulty_score(score: float) -> float:
        """
        Validate difficulty score is between 0.0 and 1.0.
        
        Args:
            score: Difficulty score to validate
            
        Returns:
            Validated difficulty score
            
        Raises:
            InvalidDifficultyScoreError: If score is out of range
        """
        if not isinstance(score, (int, float)):
            raise InvalidDifficultyScoreError(score)
        
        score = float(score)
        
        if score < Validators.MIN_DIFFICULTY or score > Validators.MAX_DIFFICULTY:
            raise InvalidDifficultyScoreError(score)
        
        return score
    
    @staticmethod
    def validate_mastery_level(level: float) -> float:
        """
        Validate mastery level is between 0.0 and 1.0.
        
        Args:
            level: Mastery level to validate
            
        Returns:
            Validated mastery level
            
        Raises:
            InvalidMasteryLevelError: If level is out of range
        """
        if not isinstance(level, (int, float)):
            raise InvalidMasteryLevelError(level)
        
        level = float(level)
        
        if level < Validators.MIN_MASTERY or level > Validators.MAX_MASTERY:
            raise InvalidMasteryLevelError(level)
        
        return level
    
    @staticmethod
    def validate_access_code(code: str) -> str:
        """
        Validate access code format (8 uppercase alphanumeric characters).
        
        Args:
            code: Access code to validate
            
        Returns:
            Validated and normalized access code
            
        Raises:
            ValueError: If code format is invalid
        """
        if not code:
            raise ValueError("Access code cannot be empty")
        
        # Remove hyphens and convert to uppercase
        normalized = code.replace("-", "").upper()
        
        if not re.match(Validators.ACCESS_CODE_PATTERN, normalized):
            raise ValueError("Access code must be 8 alphanumeric characters")
        
        return normalized
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that all required fields are present and not None.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Raises:
            MissingRequiredFieldError: If any required field is missing
        """
        for field in required_fields:
            if field not in data or data[field] is None:
                raise MissingRequiredFieldError(field)
    
    @staticmethod
    def validate_question_count(count: int, min_count: int = 1, max_count: int = 100) -> int:
        """
        Validate question count is within acceptable range.
        
        Args:
            count: Number of questions
            min_count: Minimum allowed
            max_count: Maximum allowed
            
        Returns:
            Validated question count
            
        Raises:
            ValueError: If count is out of range
        """
        if not isinstance(count, int):
            raise ValueError("Question count must be an integer")
        
        if count < min_count or count > max_count:
            raise ValueError(f"Question count must be between {min_count} and {max_count}")
        
        return count
    
    @staticmethod
    def validate_time_limit(minutes: Optional[int]) -> Optional[int]:
        """
        Validate time limit in minutes.
        
        Args:
            minutes: Time limit in minutes (can be None)
            
        Returns:
            Validated time limit
            
        Raises:
            ValueError: If time limit is invalid
        """
        if minutes is None:
            return None
        
        if not isinstance(minutes, int):
            raise ValueError("Time limit must be an integer")
        
        if minutes < 1 or minutes > 480:  # Max 8 hours
            raise ValueError("Time limit must be between 1 and 480 minutes")
        
        return minutes
    
    @staticmethod
    def sanitize_text_input(text: str, max_length: int = 10000) -> str:
        """
        Sanitize text input by removing dangerous characters and limiting length.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove null bytes and other control characters
        sanitized = text.replace('\x00', '').strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_concept_id(concept_id: str) -> str:
        """
        Validate concept ID format.
        
        Args:
            concept_id: Concept ID to validate
            
        Returns:
            Validated concept ID
            
        Raises:
            ValueError: If concept ID format is invalid
        """
        if not concept_id:
            raise ValueError("Concept ID cannot be empty")
        
        # Concept IDs should be lowercase with dots and hyphens
        pattern = r'^[a-z0-9.-]+$'
        if not re.match(pattern, concept_id):
            raise ValueError("Concept ID must contain only lowercase letters, numbers, dots, and hyphens")
        
        return concept_id


class QuestionValidator:
    """Specialized validator for question data."""
    
    @staticmethod
    def validate_question_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete question data structure.
        
        Args:
            data: Question data dictionary
            
        Returns:
            Validated question data
            
        Raises:
            Various validation errors
        """
        # Required fields
        Validators.validate_required_fields(data, [
            'question_text',
            'question_type',
            'correct_answer'
        ])
        
        # Sanitize text fields
        data['question_text'] = Validators.sanitize_text_input(data['question_text'], 5000)
        
        if 'explanation_correct' in data and data['explanation_correct']:
            data['explanation_correct'] = Validators.sanitize_text_input(
                data['explanation_correct'], 2000
            )
        
        if 'hint' in data and data['hint']:
            data['hint'] = Validators.sanitize_text_input(data['hint'], 500)
        
        # Validate difficulty score if present
        if 'difficulty_score' in data and data['difficulty_score'] is not None:
            data['difficulty_score'] = Validators.validate_difficulty_score(
                data['difficulty_score']
            )
        
        # Validate concept IDs if present
        if 'concept_ids' in data and data['concept_ids']:
            data['concept_ids'] = [
                Validators.validate_concept_id(cid) for cid in data['concept_ids']
            ]
        
        return data

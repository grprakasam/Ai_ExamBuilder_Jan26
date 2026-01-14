from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.concept import MasteryRecord
from app.models.test import Question, DifficultyEnum
import uuid


class AdaptiveDifficultyService:
    """
    Service for dynamically adjusting question difficulty based on student performance.
    Implements Zone of Proximal Development (ZPD) targeting.
    
    ZPD: The sweet spot where questions are challenging but achievable.
    Target success rate: 70-85% (Goldilocks zone)
    """
    
    # Difficulty adjustment thresholds
    TARGET_SUCCESS_RATE_MIN = 0.70  # 70%
    TARGET_SUCCESS_RATE_MAX = 0.85  # 85%
    
    # Consecutive correct/wrong needed to adjust
    CONSECUTIVE_CORRECT_THRESHOLD = 3
    CONSECUTIVE_WRONG_THRESHOLD = 2
    
    @staticmethod
    def calculate_current_difficulty(
        db: Session,
        test_id: uuid.UUID,
        concept_id: str,
        recent_questions: int = 5
    ) -> float:
        """
        Calculate the current appropriate difficulty level (0.0-1.0) for a student.
        
        Args:
            db: Database session
            test_id: Test/student identifier
            concept_id: Concept being practiced
            recent_questions: Number of recent questions to consider
        
        Returns:
            Difficulty score 0.0-1.0
        """
        mastery_record = db.query(MasteryRecord).filter(
            MasteryRecord.test_id == test_id,
            MasteryRecord.concept_id == concept_id
        ).first()
        
        if not mastery_record or mastery_record.questions_attempted < 3:
            # Start at medium difficulty (0.5) for new concepts
            return 0.5
        
        # Calculate success rate
        success_rate = mastery_record.questions_correct / mastery_record.questions_attempted
        
        # Adjust difficulty based on success rate
        if success_rate > AdaptiveDifficultyService.TARGET_SUCCESS_RATE_MAX:
            # Too easy - increase difficulty
            return min(1.0, mastery_record.current_level + 0.15)
        elif success_rate < AdaptiveDifficultyService.TARGET_SUCCESS_RATE_MIN:
            # Too hard - decrease difficulty
            return max(0.2, mastery_record.current_level - 0.15)
        else:
            # In ZPD - maintain current difficulty
            return mastery_record.current_level
    
    @staticmethod
    def should_adjust_difficulty(
        recent_results: List[bool]
    ) -> Optional[str]:
        """
        Determine if difficulty should be adjusted based on recent performance.
        
        Args:
            recent_results: List of recent answer correctness (True/False)
        
        Returns:
            'increase', 'decrease', or None
        """
        if len(recent_results) < 3:
            return None
        
        # Check for consecutive correct answers
        if recent_results[-AdaptiveDifficultyService.CONSECUTIVE_CORRECT_THRESHOLD:] == [True] * AdaptiveDifficultyService.CONSECUTIVE_CORRECT_THRESHOLD:
            return 'increase'
        
        # Check for consecutive wrong answers
        if recent_results[-AdaptiveDifficultyService.CONSECUTIVE_WRONG_THRESHOLD:] == [False] * AdaptiveDifficultyService.CONSECUTIVE_WRONG_THRESHOLD:
            return 'decrease'
        
        return None
    
    @staticmethod
    def get_difficulty_label(difficulty_score: float) -> DifficultyEnum:
        """Convert difficulty score (0.0-1.0) to difficulty enum."""
        if difficulty_score < 0.4:
            return DifficultyEnum.EASY
        elif difficulty_score < 0.7:
            return DifficultyEnum.MEDIUM
        else:
            return DifficultyEnum.HARD
    
    @staticmethod
    def calculate_zpd_range(mastery_level: float) -> tuple[float, float]:
        """
        Calculate the Zone of Proximal Development range.
        
        ZPD should be slightly above current mastery level.
        
        Args:
            mastery_level: Current mastery (0.0-1.0)
        
        Returns:
            (min_difficulty, max_difficulty) tuple
        """
        # ZPD is typically 10-20% above current level
        zpd_min = min(1.0, mastery_level + 0.05)
        zpd_max = min(1.0, mastery_level + 0.20)
        
        return (zpd_min, zpd_max)


class PersonalizedPracticeQueue:
    """
    Service for generating personalized practice question queues.
    Prioritizes weak concepts and mixes review with new learning.
    """
    
    @staticmethod
    def generate_practice_session(
        db: Session,
        test_id: uuid.UUID,
        target_questions: int = 20,
        mix_ratio: float = 0.7  # 70% weak concepts, 30% review
    ) -> List[Dict]:
        """
        Generate a personalized practice session.
        
        Strategy:
        1. Identify weak concepts (mastery < 80%)
        2. Identify concepts due for review (spaced repetition)
        3. Mix weak + review + new learning
        4. Adjust difficulty to ZPD
        
        Args:
            db: Database session
            test_id: Test/student identifier
            target_questions: Total questions to generate
            mix_ratio: Ratio of weak concepts to review
        
        Returns:
            List of question specifications to generate
        """
        # Get all mastery records for this student
        records = db.query(MasteryRecord).filter(
            MasteryRecord.test_id == test_id
        ).all()
        
        if not records:
            # New student - start with diagnostic
            return [{
                "type": "diagnostic",
                "message": "Start with a diagnostic assessment to identify your current level"
            }]
        
        # Categorize concepts
        weak_concepts = [r for r in records if r.current_level < 0.8 and not r.is_mastered]
        review_concepts = [r for r in records if r.needs_review]
        mastered_concepts = [r for r in records if r.is_mastered]
        
        # Calculate question distribution
        weak_count = int(target_questions * mix_ratio)
        review_count = target_questions - weak_count
        
        practice_queue = []
        
        # Add weak concept questions
        for i, record in enumerate(weak_concepts[:weak_count]):
            difficulty = AdaptiveDifficultyService.calculate_current_difficulty(
                db, test_id, record.concept_id
            )
            practice_queue.append({
                "concept_id": record.concept_id,
                "difficulty_score": difficulty,
                "reason": "Building mastery",
                "current_mastery": record.current_level,
                "priority": "high"
            })
        
        # Add review questions
        for i, record in enumerate(review_concepts[:review_count]):
            difficulty = AdaptiveDifficultyService.calculate_current_difficulty(
                db, test_id, record.concept_id
            )
            practice_queue.append({
                "concept_id": record.concept_id,
                "difficulty_score": difficulty,
                "reason": "Spaced repetition review",
                "current_mastery": record.current_level,
                "priority": "medium"
            })
        
        # Fill remaining with mastered concepts (maintenance)
        remaining = target_questions - len(practice_queue)
        for i, record in enumerate(mastered_concepts[:remaining]):
            difficulty = 0.7  # Keep mastered concepts challenging
            practice_queue.append({
                "concept_id": record.concept_id,
                "difficulty_score": difficulty,
                "reason": "Maintaining mastery",
                "current_mastery": record.current_level,
                "priority": "low"
            })
        
        return practice_queue
    
    @staticmethod
    def get_next_question_recommendation(
        db: Session,
        test_id: uuid.UUID,
        recent_performance: List[Dict]
    ) -> Dict:
        """
        Get real-time recommendation for next question.
        
        Args:
            db: Database session
            test_id: Test/student identifier
            recent_performance: Recent question results
        
        Returns:
            Recommendation dict with concept and difficulty
        """
        if not recent_performance:
            # First question - start with diagnostic
            return {
                "concept_id": None,
                "difficulty_score": 0.5,
                "reason": "Starting assessment"
            }
        
        # Get last concept practiced
        last_concept = recent_performance[-1].get("concept_id")
        recent_results = [p["is_correct"] for p in recent_performance[-5:]]
        
        # Check if difficulty should adjust
        adjustment = AdaptiveDifficultyService.should_adjust_difficulty(recent_results)
        
        if adjustment:
            # Continue with same concept at adjusted difficulty
            current_diff = recent_performance[-1].get("difficulty_score", 0.5)
            new_diff = current_diff + 0.1 if adjustment == 'increase' else current_diff - 0.1
            new_diff = max(0.2, min(1.0, new_diff))
            
            return {
                "concept_id": last_concept,
                "difficulty_score": new_diff,
                "reason": f"Adjusting difficulty ({adjustment})",
                "adjustment": adjustment
            }
        
        # Move to next concept in queue
        practice_queue = PersonalizedPracticeQueue.generate_practice_session(
            db, test_id, target_questions=1
        )
        
        return practice_queue[0] if practice_queue else {
            "concept_id": None,
            "difficulty_score": 0.5,
            "reason": "No recommendations available"
        }

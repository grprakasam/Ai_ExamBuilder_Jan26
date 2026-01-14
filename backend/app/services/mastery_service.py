from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.concept import MasteryRecord, Concept
import uuid


class MasteryService:
    """
    Service for calculating and updating concept mastery using the SM-2 algorithm.
    SM-2 (SuperMemo 2) is a spaced repetition algorithm for optimal learning retention.
    """
    
    # Mastery thresholds
    MASTERY_THRESHOLD = 0.8  # 80% = mastered
    PROFICIENT_THRESHOLD = 0.6  # 60% = proficient
    DEVELOPING_THRESHOLD = 0.4  # 40% = developing
    
    @staticmethod
    def calculate_mastery_level(correct: int, total: int) -> float:
        """Calculate mastery level (0.0-1.0) based on correct/total ratio."""
        if total == 0:
            return 0.0
        return min(1.0, correct / total)
    
    @staticmethod
    def update_sm2_parameters(
        quality: int,  # 0-5 (0=complete blackout, 5=perfect response)
        ease_factor: float,
        interval_days: int,
        repetitions: int
    ) -> tuple[float, int, int]:
        """
        Update SM-2 parameters based on response quality.
        
        Args:
            quality: Response quality (0-5)
                5 - perfect response
                4 - correct response after a hesitation
                3 - correct response recalled with serious difficulty
                2 - incorrect response; correct one seemed easy to recall
                1 - incorrect response; correct one remembered
                0 - complete blackout
            ease_factor: Current ease factor (1.3 minimum)
            interval_days: Current interval in days
            repetitions: Number of successful repetitions
        
        Returns:
            (new_ease_factor, new_interval_days, new_repetitions)
        """
        # Update ease factor
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(1.3, new_ease_factor)  # Minimum ease factor is 1.3
        
        # Update repetitions and interval
        if quality < 3:
            # Incorrect response - reset
            new_repetitions = 0
            new_interval_days = 1
        else:
            # Correct response
            new_repetitions = repetitions + 1
            if new_repetitions == 1:
                new_interval_days = 1
            elif new_repetitions == 2:
                new_interval_days = 6
            else:
                new_interval_days = int(interval_days * new_ease_factor)
        
        return new_ease_factor, new_interval_days, new_repetitions
    
    @staticmethod
    def calculate_quality_score(
        is_correct: bool,
        time_taken_seconds: float,
        expected_time_seconds: float = 60.0,
        had_hint: bool = False
    ) -> int:
        """
        Convert answer correctness and speed into SM-2 quality score (0-5).
        
        Args:
            is_correct: Whether the answer was correct
            time_taken_seconds: Time taken to answer
            expected_time_seconds: Expected time for this difficulty
            had_hint: Whether student used a hint
        
        Returns:
            Quality score 0-5
        """
        if not is_correct:
            return 0 if time_taken_seconds > expected_time_seconds * 2 else 1
        
        # Correct answer
        if had_hint:
            return 3  # Correct but needed help
        
        time_ratio = time_taken_seconds / expected_time_seconds
        if time_ratio < 0.5:
            return 5  # Perfect - fast and correct
        elif time_ratio < 1.0:
            return 4  # Good - correct at normal speed
        else:
            return 3  # Okay - correct but slow
    
    @staticmethod
    def update_mastery_record(
        db: Session,
        test_id: uuid.UUID,
        concept_id: str,
        is_correct: bool,
        time_taken_seconds: float,
        had_hint: bool = False
    ) -> MasteryRecord:
        """
        Update or create a mastery record for a concept.
        
        Args:
            db: Database session
            test_id: Test ID (for PII-minimal tracking)
            concept_id: Concept identifier
            is_correct: Whether the answer was correct
            time_taken_seconds: Time taken to answer
            had_hint: Whether student used a hint
        
        Returns:
            Updated MasteryRecord
        """
        # Get or create mastery record
        record = db.query(MasteryRecord).filter(
            MasteryRecord.test_id == test_id,
            MasteryRecord.concept_id == concept_id
        ).first()
        
        if not record:
            record = MasteryRecord(
                test_id=test_id,
                concept_id=concept_id,
                last_practiced=datetime.now(),
                next_review_due=datetime.now() + timedelta(days=1)
            )
            db.add(record)
        
        # Update attempt counts
        record.questions_attempted += 1
        if is_correct:
            record.questions_correct += 1
            record.streak_current += 1
            record.streak_best = max(record.streak_best, record.streak_current)
        else:
            record.streak_current = 0
        
        # Calculate mastery level
        record.current_level = MasteryService.calculate_mastery_level(
            record.questions_correct,
            record.questions_attempted
        )
        
        # Update mastery status
        if record.current_level >= MasteryService.MASTERY_THRESHOLD and not record.is_mastered:
            record.is_mastered = True
            record.mastery_achieved_date = datetime.now()
        elif record.current_level < MasteryService.MASTERY_THRESHOLD:
            record.is_mastered = False
        
        # Calculate quality score for SM-2
        quality = MasteryService.calculate_quality_score(
            is_correct,
            time_taken_seconds,
            had_hint=had_hint
        )
        
        # Update SM-2 parameters
        new_ease, new_interval, new_reps = MasteryService.update_sm2_parameters(
            quality,
            record.ease_factor,
            record.interval_days,
            record.repetitions
        )
        
        record.ease_factor = new_ease
        record.interval_days = new_interval
        record.repetitions = new_reps
        record.last_practiced = datetime.now()
        record.next_review_due = datetime.now() + timedelta(days=new_interval)
        record.needs_review = False
        
        # Update learning velocity
        if record.avg_time_to_correct is None:
            record.avg_time_to_correct = time_taken_seconds if is_correct else None
        elif is_correct:
            # Exponential moving average
            record.avg_time_to_correct = 0.7 * record.avg_time_to_correct + 0.3 * time_taken_seconds
        
        db.commit()
        db.refresh(record)
        
        return record
    
    @staticmethod
    def get_concepts_due_for_review(
        db: Session,
        test_id: uuid.UUID,
        limit: int = 10
    ) -> List[MasteryRecord]:
        """Get concepts that are due for review."""
        now = datetime.now()
        return db.query(MasteryRecord).filter(
            MasteryRecord.test_id == test_id,
            MasteryRecord.next_review_due <= now
        ).order_by(MasteryRecord.next_review_due).limit(limit).all()
    
    @staticmethod
    def get_mastery_summary(
        db: Session,
        test_id: uuid.UUID
    ) -> Dict:
        """Get overall mastery summary for a student."""
        records = db.query(MasteryRecord).filter(
            MasteryRecord.test_id == test_id
        ).all()
        
        if not records:
            return {
                "total_concepts": 0,
                "mastered": 0,
                "proficient": 0,
                "developing": 0,
                "struggling": 0,
                "overall_mastery": 0.0,
                "best_streak": 0,
                "concepts_due_review": 0
            }
        
        mastered = sum(1 for r in records if r.current_level >= MasteryService.MASTERY_THRESHOLD)
        proficient = sum(1 for r in records if MasteryService.PROFICIENT_THRESHOLD <= r.current_level < MasteryService.MASTERY_THRESHOLD)
        developing = sum(1 for r in records if MasteryService.DEVELOPING_THRESHOLD <= r.current_level < MasteryService.PROFICIENT_THRESHOLD)
        struggling = sum(1 for r in records if r.current_level < MasteryService.DEVELOPING_THRESHOLD)
        
        overall_mastery = sum(r.current_level for r in records) / len(records)
        best_streak = max((r.streak_best for r in records), default=0)
        concepts_due = sum(1 for r in records if r.next_review_due <= datetime.now())
        
        return {
            "total_concepts": len(records),
            "mastered": mastered,
            "proficient": proficient,
            "developing": developing,
            "struggling": struggling,
            "overall_mastery": round(overall_mastery, 2),
            "best_streak": best_streak,
            "concepts_due_review": concepts_due
        }

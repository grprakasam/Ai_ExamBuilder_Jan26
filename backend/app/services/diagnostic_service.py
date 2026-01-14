from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.models.concept import Concept, MasteryRecord
from app.models.test import Question
from app.services.question_generator import QuestionGenerator
from app.data.concept_taxonomy import get_concepts_by_grade, get_prerequisite_chain
import uuid


class DiagnosticService:
    """
    Service for creating and managing diagnostic assessments.
    Diagnostic tests identify knowledge gaps and create personalized learning paths.
    """
    
    def __init__(self):
        self.question_generator = QuestionGenerator()
    
    async def create_diagnostic_test(
        self,
        db: Session,
        grade_level: int,
        subject: str,
        exam_standard: str = "NCDPI"
    ) -> Dict:
        """
        Create an adaptive diagnostic test to assess current knowledge.
        
        Strategy:
        1. Start with grade-level appropriate concepts
        2. Ask 2-3 questions per concept
        3. Adjust difficulty based on responses
        4. Identify knowledge gaps
        
        Returns:
            Dict with test_id, questions, and concept coverage
        """
        # Get concepts for this grade level
        concepts = get_concepts_by_grade(grade_level)
        
        # Select key concepts to assess (limit to 5-7 for 10-15 minute test)
        key_concepts = self._select_key_concepts(concepts, limit=6)
        
        # Generate 2 questions per concept (12 total)
        diagnostic_questions = []
        concept_coverage = {}
        
        for concept in key_concepts:
            # Generate questions at varying difficulties
            questions = await self._generate_diagnostic_questions(
                concept=concept,
                grade_level=grade_level,
                subject=subject,
                count=2
            )
            diagnostic_questions.extend(questions)
            concept_coverage[concept["concept_id"]] = {
                "name": concept["name"],
                "question_count": len(questions)
            }
        
        return {
            "questions": diagnostic_questions,
            "concept_coverage": concept_coverage,
            "total_questions": len(diagnostic_questions),
            "estimated_minutes": len(diagnostic_questions) * 1.5,  # 1.5 min per question
            "purpose": "diagnostic"
        }
    
    def _select_key_concepts(self, concepts: List[Dict], limit: int = 6) -> List[Dict]:
        """
        Select the most important concepts to assess.
        Prioritize foundational concepts with many dependents.
        """
        # Sort by number of prerequisites (foundational first)
        sorted_concepts = sorted(
            concepts,
            key=lambda c: len(c.get("prerequisite_concept_ids", []))
        )
        
        # Take a mix of foundational and advanced
        foundational = sorted_concepts[:limit//2]
        advanced = sorted_concepts[-(limit - limit//2):]
        
        return foundational + advanced
    
    async def _generate_diagnostic_questions(
        self,
        concept: Dict,
        grade_level: int,
        subject: str,
        count: int = 2
    ) -> List[Dict]:
        """Generate diagnostic questions for a specific concept."""
        # Generate questions at medium difficulty for diagnostic
        questions = await self.question_generator.generate_questions(
            grade=grade_level,
            subject=subject,
            standard=concept["name"],
            count=count,
            q_type="mcq",
            difficulty="medium"
        )
        
        # Tag questions with concept_id
        for q in questions:
            q["concept_ids"] = [concept["concept_id"]]
            q["is_diagnostic"] = True
        
        return questions
    
    def analyze_diagnostic_results(
        self,
        db: Session,
        test_id: uuid.UUID,
        answers: Dict[int, str],
        questions: List[Question]
    ) -> Dict:
        """
        Analyze diagnostic test results to create a learning profile.
        
        Returns:
            Learning profile with strengths, weaknesses, and recommended path
        """
        concept_performance = {}
        
        # Analyze performance per concept
        for idx, question in enumerate(questions):
            if not question.concept_ids:
                continue
            
            user_answer = answers.get(idx)
            is_correct = user_answer == question.correct_answer
            
            for concept_id in question.concept_ids:
                if concept_id not in concept_performance:
                    concept_performance[concept_id] = {
                        "attempted": 0,
                        "correct": 0,
                        "questions": []
                    }
                
                concept_performance[concept_id]["attempted"] += 1
                if is_correct:
                    concept_performance[concept_id]["correct"] += 1
                concept_performance[concept_id]["questions"].append({
                    "question_id": question.id,
                    "is_correct": is_correct
                })
        
        # Calculate mastery levels
        for concept_id, perf in concept_performance.items():
            perf["mastery_level"] = perf["correct"] / perf["attempted"] if perf["attempted"] > 0 else 0.0
        
        # Categorize concepts
        mastered = {k: v for k, v in concept_performance.items() if v["mastery_level"] >= 0.8}
        proficient = {k: v for k, v in concept_performance.items() if 0.6 <= v["mastery_level"] < 0.8}
        needs_work = {k: v for k, v in concept_performance.items() if v["mastery_level"] < 0.6}
        
        # Determine starting point (lowest mastery concept with prerequisites met)
        recommended_start = self._find_optimal_starting_point(
            needs_work,
            mastered
        )
        
        return {
            "overall_mastery": sum(p["mastery_level"] for p in concept_performance.values()) / len(concept_performance) if concept_performance else 0.0,
            "concepts_assessed": len(concept_performance),
            "mastered": list(mastered.keys()),
            "proficient": list(proficient.keys()),
            "needs_work": list(needs_work.keys()),
            "recommended_starting_point": recommended_start,
            "detailed_performance": concept_performance
        }
    
    def _find_optimal_starting_point(
        self,
        needs_work: Dict,
        mastered: Dict
    ) -> Optional[str]:
        """
        Find the best concept to start learning.
        Choose the concept with lowest mastery whose prerequisites are met.
        """
        if not needs_work:
            return None
        
        # Sort by mastery level (lowest first)
        sorted_concepts = sorted(
            needs_work.items(),
            key=lambda x: x[1]["mastery_level"]
        )
        
        # Find first concept whose prerequisites are mastered
        for concept_id, _ in sorted_concepts:
            prereqs = get_prerequisite_chain(concept_id)
            if all(p in mastered for p in prereqs):
                return concept_id
        
        # If no concept has all prerequisites, return the lowest mastery one
        return sorted_concepts[0][0] if sorted_concepts else None
    
    def create_personalized_learning_path(
        self,
        db: Session,
        diagnostic_results: Dict,
        grade_level: int
    ) -> List[Dict]:
        """
        Create a personalized learning path based on diagnostic results.
        
        Returns:
            Ordered list of concepts to learn with estimated time
        """
        needs_work = diagnostic_results["needs_work"]
        mastered = diagnostic_results["mastered"]
        
        # Get all concepts for grade level
        all_concepts = get_concepts_by_grade(grade_level)
        
        # Build learning path
        learning_path = []
        
        # Start with recommended starting point
        current = diagnostic_results["recommended_starting_point"]
        if current:
            learning_path.append({
                "concept_id": current,
                "reason": "Starting point - foundational concept that needs work",
                "priority": "high"
            })
        
        # Add other concepts that need work, ordered by prerequisites
        for concept_id in needs_work:
            if concept_id != current:
                learning_path.append({
                    "concept_id": concept_id,
                    "reason": "Identified gap in diagnostic",
                    "priority": "medium"
                })
        
        # Add advanced concepts not yet assessed
        assessed_ids = set(mastered + diagnostic_results["proficient"] + needs_work)
        for concept in all_concepts:
            if concept["concept_id"] not in assessed_ids:
                learning_path.append({
                    "concept_id": concept["concept_id"],
                    "reason": "Advanced topic for future learning",
                    "priority": "low"
                })
        
        return learning_path

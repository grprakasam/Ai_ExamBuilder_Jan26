from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.config import settings
import json


class QuestionGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def _build_prompt(self, grade: int, subject: str, standard: str, count: int, q_type: str, difficulty: str) -> str:
        type_instruction = ""
        if q_type == "open_ended":
            type_instruction = "These should be open-ended, short-answer questions. Do NOT provide options A, B, C, D. Instead, provide a 'correct_answer' which is a model response or rubric."
        else:
            type_instruction = "These must be Multiple Choice Questions (MCQ). Provide exactly 4 choices labeled A, B, C, D. Each wrong answer should be designed to reveal a specific misconception."

        return f"""
You are a learning-centered assessment designer creating questions that TEACH, not just test.

Create {count} questions for:
• Grade: {grade}
• Subject: {subject}
• Standard: {standard}
• Question Type: {q_type}
• Difficulty: {difficulty}

CRITICAL: Every question is a TEACHING MOMENT. Your goal is to help students learn, not just evaluate them.

Requirements:
1. {type_instruction}
2. Use grade-appropriate vocabulary and real-world contexts
3. Align to educational standards for Grade {grade}

For EACH question, provide COMPLETE learning support:

**Question Design:**
- Clear, unambiguous question text
- For MCQ: 4 options where each wrong answer reveals a specific misconception

**Learning Metadata:**
- concept_ids: 2-3 specific concepts this question addresses (e.g., ["fractions.adding", "common-denominators"])
- prerequisite_concepts: What students must know first (e.g., ["fractions.basics", "multiplication"])
- learning_objective: One sentence: "Students will be able to..."
- bloom_level: One of: remember, understand, apply, analyze, evaluate, create
- difficulty_score: 0.0-1.0 (0.2=very easy, 0.5=grade-level, 0.8=challenging)

**Rich Feedback (CRITICAL - this is how students learn):**
- explanation_correct: Explain WHY the correct answer is correct (teach the concept)
- explanation_wrong: For EACH wrong option, explain why it's wrong and what misconception it represents
  Example: {{"A": "This adds numerators AND denominators, which doesn't work because...", "B": "This subtracts instead of adds..."}}
- common_misconceptions: List 1-2 common mistakes students make on this type of problem
- worked_example: Step-by-step solution showing the thinking process
- hint: A guiding question or reminder that helps without giving away the answer

Output ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "sequence": 1,
      "question_text": "What is 3/4 + 1/2?",
      "question_type": "{q_type}",
      "options": {{"A": "5/4", "B": "4/6", "C": "1/3", "D": "2/3"}},
      "correct_answer": "A",
      
      "concept_ids": ["fractions.adding", "common-denominators"],
      "prerequisite_concepts": ["fractions.basics", "equivalent-fractions"],
      "learning_objective": "Students will be able to add fractions with different denominators by finding a common denominator.",
      "bloom_level": "apply",
      "difficulty_score": 0.5,
      
      "explanation_correct": "To add fractions, we need a common denominator. Converting 1/2 to 2/4, we get 3/4 + 2/4 = 5/4 or 1 1/4.",
      "explanation_wrong": {{
        "B": "This incorrectly adds both numerators (3+1=4) AND denominators (4+2=6). We can only add numerators when denominators are the same.",
        "C": "This subtracts instead of adds. Check the operation sign.",
        "D": "This might come from incorrectly simplifying. The actual sum is 5/4."
      }},
      "common_misconceptions": [
        "Students often add both numerators and denominators",
        "Students forget to find a common denominator first"
      ],
      "worked_example": "Step 1: Find common denominator (4)\\nStep 2: Convert 1/2 to 2/4\\nStep 3: Add numerators: 3/4 + 2/4 = 5/4\\nStep 4: Simplify if needed: 5/4 = 1 1/4",
      "hint": "Before adding fractions, what do the denominators need to be?"
    }}
  ]
}}
"""

    async def generate_questions(self, grade: int, subject: str, standard: str, count: int, q_type: str, difficulty: str) -> List[Dict[str, Any]]:
        prompt = self._build_prompt(grade, subject, standard, count, q_type, difficulty)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a learning-centered educational content creator. Your questions must TEACH, not just test. Every question should include complete learning support: concept tags, Bloom level, detailed explanations for ALL answer choices, common misconceptions, worked examples, and helpful hints. Respond with valid JSON only, no markdown formatting."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content

        # Extract JSON from markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)
        return data.get("questions", [])

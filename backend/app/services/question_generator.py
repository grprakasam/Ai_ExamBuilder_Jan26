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
            type_instruction = "These must be Multiple Choice Questions (MCQ). Provide exactly 4 choices labeled A, B, C, D."

        return f"""
You are an NCDPI-aligned assessment designer.
Create a North Carolina End-of-Grade (EOG) style practice test for:

• Grade: Grade {grade}
• Subject: {subject}
• Strand / Standard Focus: {standard}
• Number of Questions: {count}
• Question Type: {q_type}
• Difficulty: {difficulty} (EOG-aligned)

Follow these STRICT requirements:
1. Alignment & Rigor: Questions must be aligned to NCDPI standards for the specified grade.
2. Question Design: Use real EOG-style wording and structure. Use grade-appropriate vocabulary.
3. {type_instruction}
4. Formatting: Output ONLY valid JSON, no other text.

Format the output as a JSON object with a list of questions:
{{
  "questions": [
    {{
      "sequence": 1,
      "question_text": "...",
      "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correct_answer": "...",
      "explanation": "...",
      "cognitive_level": "Recall",
      "question_type": "{q_type}"
    }}
  ]
}}
"""

    async def generate_questions(self, grade: int, subject: str, standard: str, count: int, q_type: str, difficulty: str) -> List[Dict[str, Any]]:
        prompt = self._build_prompt(grade, subject, standard, count, q_type, difficulty)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional assessment creator for NCDPI tests. You must respond with valid JSON only, no markdown formatting."},
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

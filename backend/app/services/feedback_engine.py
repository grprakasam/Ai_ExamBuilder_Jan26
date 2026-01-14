from typing import List, Dict, Any
from openai import AsyncOpenAI
from app.config import settings
import json

class FeedbackEngine:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def evaluate_responses(self, questions: List[Dict], user_answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate open-ended or complex MCQ responses using AI.
        """
        # Filter for open-ended questions only for now, or all if we want rigorous feedback
        evaluation_data = []
        for i, q in enumerate(questions):
            ans = user_answers.get(str(i))
            evaluation_data.append({
                "index": i + 1,
                "question": q.get("question_text"),
                "expected": q.get("correct_answer"),
                "student_answer": ans,
                "type": q.get("question_type")
            })

        prompt = f"""
You are an expert academic evaluator for {questions[0].get('exam_standard', 'standardized')} assessments. 
Analyze the student's performance on the following questions.
For each question, provide:
1. Score (0 to 1)
2. Professional, constructive, and growth-oriented feedback 
3. A "hint" or "suggestion" for improvement if the answer is incorrect or partial.

Input Data:
{json.dumps(evaluation_data, indent=2)}

Format the output as a JSON object:
{{
  "overall_summary": "...",
  "evaluations": [
    {{
      "index": 1,
      "score": 1.0, 
      "feedback": "...",
      "suggestion": "..."
    }}
  ]
}}
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional educational evaluator providing constructive feedback to students."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )

        
        return json.loads(response.choices[0].message.content)

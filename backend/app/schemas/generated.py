from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.test import QuestionBase

class GeneratedQuestion(QuestionBase):
    model_config = ConfigDict(extra="ignore")
    sequence: int = Field(ge=1)
    question_text: str = Field(min_length=1)
    correct_answer: str = Field(min_length=1)

    @model_validator(mode="after")
    def valid_answer(self):
        if self.question_type.value == "mcq":
            if not self.options or len(self.options) != 4 or self.correct_answer not in self.options:
                raise ValueError("MCQs require four options and an answer matching an option key")
        elif self.question_type.value != "open_ended":
            raise ValueError("Each generated question must be MCQ or open-ended")
        return self

class GeneratedQuestions(BaseModel):
    questions: list[GeneratedQuestion] = Field(min_length=1, max_length=50)

    @model_validator(mode="after")
    def unique_sequences(self):
        if [q.sequence for q in self.questions] != list(range(1, len(self.questions) + 1)):
            raise ValueError("Question sequences must be consecutive, starting at one")
        return self

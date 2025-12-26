from typing import List
from pydantic import BaseModel


class MCQOption(BaseModel):
    option_id: str
    text: str
    score: int


class MCQQuestion(BaseModel):
    question_id: str
    question: str
    options: List[MCQOption]

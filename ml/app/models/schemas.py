from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal

class Example(BaseModel):
    input: str
    output: str

class Task(BaseModel):
    title: str
    description: str
    input_format: str
    output_format: str
    examples: List[Example]
    constraints: Optional[List[str]] = None
    difficulty: Literal["easy", "medium", "hard"]
    hidden_tests: Optional[List[str]] = None  # Только inputs (для обратной совместимости)
    hidden_tests_full: Optional[List[Dict[str, str]]] = None  # Полные тесты с input и output
    hints: Optional[List[Dict[str, Any]]] = None  # Подсказки трех уровней
    canonical_solution: Optional[str] = None  # Эталонное решение на Python
    canonical_solutions: Optional[Dict[str, str]] = None  # Эталонные решения на разных языках

class TaskGenerationRequest(BaseModel):
    difficulty: Literal["easy", "medium", "hard"]
    topic: Optional[str] = None
    language: Optional[str] = None

class EvaluationRequest(BaseModel):
    code: str
    task_difficulty: Literal["easy", "medium", "hard"]
    task_description: str
    hidden_tests: List[str] # Inputs for hidden tests
    
class EvaluationResult(BaseModel):
    correctness_score: float # 0.0 to 1.0
    efficiency_score: float # 0.0 to 1.0
    clean_code_score: float # 0.0 to 1.0
    feedback: str
    passed: bool

class AdaptiveLevelRequest(BaseModel):
    current_difficulty: Literal["easy", "medium", "hard"]
    is_passed: bool
    bad_attempts: int = 0
    total_time_seconds: float = 0.0

class AdaptiveLevelResponse(BaseModel):
    next_difficulty: Literal["easy", "medium", "hard"]
    reason: str

class CommunicationRequest(BaseModel):
    problem_description: str
    user_explanation: str
    code: Optional[str] = None

class CommunicationResponse(BaseModel):
    communication_score: float
    feedback: str

class FollowUpRequest(BaseModel):
    problem_description: str
    code: str

class ScoringRequest(BaseModel):
    difficulty: Literal["easy", "medium", "hard"]
    tests_passed: int
    total_tests: int
    time_taken_seconds: float
    code_quality_score: float  # 0-100
    communication_score: float  # 0-100
    hints_used: Optional[List[Literal["surface", "medium", "deep"]]] = []  # Использованные подсказки

class ScoringResponse(BaseModel):
    final_score: float

class Hint(BaseModel):
    level: Literal["surface", "medium", "deep"]
    content: str
    penalty: float  # Штраф в баллах за использование подсказки

class HintRequest(BaseModel):
    task_description: str
    task_difficulty: Literal["easy", "medium", "hard"]
    hint_level: Literal["surface", "medium", "deep"]

class HintResponse(BaseModel):
    hint: str
    penalty: float
    remaining_hints: int

class GenerateHintsRequest(BaseModel):
    task_description: str
    task_difficulty: Literal["easy", "medium", "hard"]
    input_format: str
    output_format: str
    examples: List[Example]

class GenerateHintsResponse(BaseModel):
    hints: List[Hint]

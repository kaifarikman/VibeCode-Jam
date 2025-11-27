"""
API эндпоинты для ML микросервиса VibeCode Jam.

Этот модуль содержит все REST API эндпоинты для:
- Генерации задач
- Оценки решений
- Адаптивной сложности
- Коммуникационных навыков
- Подсчёта баллов
- Анти-чит проверки
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    TaskGenerationRequest, Task,
    EvaluationRequest, EvaluationResult,
    AdaptiveLevelRequest, AdaptiveLevelResponse,
    CommunicationRequest, CommunicationResponse,
    FollowUpRequest, ScoringRequest, ScoringResponse,
    GenerateHintsRequest, GenerateHintsResponse
)
from app.services.task_generator import task_generator
from app.services.evaluator import evaluator
from app.services.adaptive_engine import adaptive_engine
from app.services.communication import communication_service
from app.services.scoring import scoring_service
from app.services.anti_cheat import anti_cheat_service
from app.services.hint_service import hint_service
from pydantic import BaseModel

router = APIRouter()

class AntiCheatRequest(BaseModel):
    """Запрос на проверку кода на плагиат."""
    code: str
    problem_description: str

@router.post("/generate-task", response_model=Task)
async def generate_task(request: TaskGenerationRequest):
    """Генерирует новую задачу заданного уровня сложности."""
    try:
        task = await task_generator.generate_task(request.difficulty)
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", response_model=EvaluationResult)
async def evaluate_solution(request: EvaluationRequest):
    """Оценивает решение кода: запускает тесты и анализирует качество."""
    try:
        result = await evaluator.evaluate_submission(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adaptive-engine", response_model=AdaptiveLevelResponse)
async def get_next_level(request: AdaptiveLevelRequest):
    """Определяет следующий уровень сложности на основе результатов."""
    try:
        result = adaptive_engine.determine_next_level(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/communication/evaluate", response_model=CommunicationResponse)
async def evaluate_communication(request: CommunicationRequest):
    """Оценивает объяснение решения кандидатом."""
    try:
        result = await communication_service.evaluate_explanation(
            request.problem_description,
            request.user_explanation,
            request.code
        )
        return CommunicationResponse(
            communication_score=result.get("communication_score", 0.0),
            feedback=result.get("feedback", "Обратная связь не предоставлена")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/communication/follow-up")
async def get_follow_up(request: FollowUpRequest):
    """Генерирует дополнительный вопрос для интервью."""
    try:
        question = await communication_service.generate_followup_question(
            request.problem_description,
            request.code
        )
        return {"question": question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/score", response_model=ScoringResponse)
async def calculate_score(request: ScoringRequest):
    """Рассчитывает итоговый взвешенный балл за интервью."""
    try:
        final_score = scoring_service.calculate_final_score(
            difficulty=request.difficulty,
            tests_passed=request.tests_passed,
            total_tests=request.total_tests,
            time_taken_seconds=request.time_taken_seconds,
            code_quality_score=request.code_quality_score,
            communication_score=request.communication_score,
            hints_used=request.hints_used
        )
        return ScoringResponse(final_score=final_score)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/anti-cheat/check")
async def check_cheat(request: AntiCheatRequest):
    """Проверяет код на плагиат и AI-генерацию."""
    try:
        result = await anti_cheat_service.check_submission(request.code, request.problem_description)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-task-mock", response_model=Task)
async def generate_task_mock(request: TaskGenerationRequest):
    """Генерирует mock задачу для тестирования без LLM."""
    mock_task = Task(
        title="Найти максимальный элемент в массиве",
        description="Дан массив целых чисел. Найдите максимальный элемент в массиве.",
        input_format="Первая строка содержит число n - размер массива. Вторая строка содержит n целых чисел через пробел.",
        output_format="Выведите максимальный элемент массива.",
        examples=[
            {"input": "5\n1 3 7 2 9", "output": "9"},
            {"input": "3\n-1 -5 -2", "output": "-1"}
        ],
        constraints=["1 ≤ n ≤ 1000", "-10^9 ≤ элементы массива ≤ 10^9"],
        difficulty=request.difficulty,
        hidden_tests=["10\n1 2 3 4 5 6 7 8 9 10", "1\n42", "4\n-10 -20 -5 -15"]
    )
    return mock_task

@router.post("/hints/generate", response_model=GenerateHintsResponse)
async def generate_hints(request: GenerateHintsRequest):
    """Генерирует три уровня подсказок для задачи."""
    try:
        hints = await hint_service.generate_hints(
            task_description=request.task_description,
            task_difficulty=request.task_difficulty,
            input_format=request.input_format,
            output_format=request.output_format,
            examples=[ex.dict() for ex in request.examples]
        )
        return GenerateHintsResponse(hints=hints)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

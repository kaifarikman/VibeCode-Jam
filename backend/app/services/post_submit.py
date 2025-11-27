"""Post-submit processing: ML evaluation, anti-cheat, communication, adaptive engine"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import uuid
from datetime import datetime

from sqlalchemy import select

from app.database import async_session_factory
from app.models import Execution, Task, TaskSolution, TaskCommunication, UserContestTasks
from app.services.ml_client import ml_client

logger = logging.getLogger(__name__)


async def process_post_submit(execution_id: uuid.UUID) -> None:
    async with async_session_factory() as session:
        execution = await session.get(Execution, execution_id)
        if (
            not execution
            or not execution.is_submit
            or execution.status != 'completed'
            or execution.result is None
        ):
            return

        solution = await session.scalar(
            select(TaskSolution).where(TaskSolution.execution_id == execution_id)
        )
        if not solution:
            return

        task = await session.get(Task, execution.task_id) if execution.task_id else None

        # Evaluate code quality
        if task and solution.ml_correctness is None:
            await _evaluate_code(session, solution, task)

        # Anti-cheat
        if task and solution.anti_cheat_flag is None:
            await _run_anti_cheat(session, solution, task)

        # Communication prompt
        await _ensure_communication_entry(session, execution, solution, task)

        # Adaptive difficulty
        await _update_adaptive_recommendation(session, execution, solution, task)

        await session.commit()


async def _evaluate_code(session, solution: TaskSolution, task: Task) -> None:
    try:
        hidden_tests = []
        if task.hidden_tests:
            try:
                parsed = json.loads(task.hidden_tests)
                if isinstance(parsed, list):
                    for test in parsed:
                        if isinstance(test, dict):
                            hidden_tests.append(test.get('input', ''))
                        elif isinstance(test, str):
                            hidden_tests.append(test)
            except json.JSONDecodeError:
                logger.warning('Failed to parse hidden tests for task %s', task.id)
        evaluation = await ml_client.evaluate_code(
            code=solution.solution_code,
            task_difficulty=task.difficulty or 'medium',
            task_description=task.description or '',
            hidden_tests=hidden_tests,
        )
        solution.ml_correctness = evaluation.get('correctness_score')
        solution.ml_efficiency = evaluation.get('efficiency_score')
        solution.ml_clean_code = evaluation.get('clean_code_score')
        solution.ml_feedback = evaluation.get('feedback')
        solution.ml_passed = evaluation.get('passed')
    except Exception as exc:  # noqa: BLE001
        logger.exception('Failed to evaluate code via ML: %s', exc)


async def _run_anti_cheat(session, solution: TaskSolution, task: Task) -> None:
    try:
        result = await ml_client.check_anti_cheat(
            code=solution.solution_code,
            problem_description=task.description or '',
        )
        solution.anti_cheat_flag = result.get('is_suspicious')
        solution.anti_cheat_reason = result.get('reason')
    except Exception as exc:  # noqa: BLE001
        logger.exception('Failed to run anti-cheat: %s', exc)


async def _ensure_communication_entry(session, execution: Execution, solution: TaskSolution, task: Task | None) -> None:
    if not task:
        return
    existing = await session.scalar(
        select(TaskCommunication)
        .where(TaskCommunication.solution_id == solution.id)
        .order_by(TaskCommunication.created_at.desc())
    )
    if existing:
        return
    question_text: str | None = None
    try:
        question = await ml_client.request_follow_up(
            problem_description=task.description or '',
            code=solution.solution_code,
        )
        if question:
            question_text = question.strip()
    except Exception as exc:  # noqa: BLE001
        logger.exception('Failed to request follow-up question: %s', exc)
    if not question_text:
        question_text = _build_default_question(task)
    if not question_text:
        return
    communication = TaskCommunication(
        user_id=execution.user_id,
        task_id=execution.task_id,
        vacancy_id=execution.vacancy_id,
        solution_id=solution.id,
        question=question_text,
        status='pending',
    )
    session.add(communication)


async def _update_adaptive_recommendation(session, execution: Execution, solution: TaskSolution, task: Task | None) -> None:
    if not (execution.vacancy_id and execution.task_id and task):
        return
    binding = await session.scalar(
        select(UserContestTasks).where(
            UserContestTasks.user_id == execution.user_id,
            UserContestTasks.vacancy_id == execution.vacancy_id,
        )
    )
    if not binding:
        return
    # Count bad attempts
    stmt = select(Execution).where(
        Execution.user_id == execution.user_id,
        Execution.task_id == execution.task_id,
        Execution.vacancy_id == execution.vacancy_id,
        Execution.is_submit.is_(True),
        Execution.id != execution.id,
    )
    executions = await session.scalars(stmt)
    bad_attempts = 0
    for exec_item in executions:
        verdict = None
        if exec_item.result and isinstance(exec_item.result, dict):
            verdict = exec_item.result.get('verdict')
        if verdict != 'ACCEPTED':
            bad_attempts += 1

    total_time = None
    if execution.started_at and execution.completed_at:
        delta = execution.completed_at - execution.started_at
        total_time = delta.total_seconds()

    try:
        adaptive = await ml_client.adaptive_next_level(
            current_difficulty=task.difficulty or 'medium',
            is_passed=solution.status == 'solved',
            bad_attempts=bad_attempts,
            total_time_seconds=total_time or 0,
        )
        binding.next_difficulty = adaptive.get('next_difficulty')
        binding.next_reason = adaptive.get('reason')
        await _swap_task_if_needed(session, binding, solution.task_id, adaptive.get('next_difficulty'))
    except Exception as exc:  # noqa: BLE001
        logger.exception('Failed to update adaptive difficulty: %s', exc)


async def _swap_task_if_needed(session, binding: UserContestTasks, solved_task_id: uuid.UUID, target_difficulty: str | None) -> None:
    if not target_difficulty:
        return
    if solved_task_id not in binding.task_ids:
        return
    stmt = select(Task).where(
        Task.difficulty == target_difficulty,
        (Task.vacancy_id == binding.vacancy_id) | (Task.vacancy_id.is_(None)),
        Task.id.notin_(binding.task_ids),
    )
    candidates = await session.scalars(stmt)
    new_task = None
    for candidate in candidates:
        new_task = candidate
        break
    if not new_task:
        return
    idx = binding.task_ids.index(solved_task_id)
    binding.task_ids[idx] = new_task.id


def schedule_post_submit(execution_id: uuid.UUID) -> None:
    asyncio.create_task(process_post_submit(execution_id))


def _build_default_question(task: Task) -> str | None:
    """Возвращает дефолтный follow-up вопрос, если ML недоступен."""
    title = (task.title or '').strip()
    if not title:
        description = (task.description or '').strip()
        if description:
            title = description.split('\n')[0][:80].strip()
    if not title:
        title = 'этой задачи'
    templates = [
        'Объясните временную и пространственную сложность вашего решения для задачи «{title}».',
        'Какие граничные случаи вы проверили в задаче «{title}» и могут ли быть ещё проблемные сценарии?',
        'Если входные данные для задачи «{title}» увеличатся в 10 раз, что произойдёт с производительностью решения?',
        'Предложите оптимизацию для вашего решения задачи «{title}» и оцените её сложность.',
    ]
    return random.choice(templates).format(title=title)


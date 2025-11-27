"""Executor Service - Микросервис для выполнения кода в Docker"""

import asyncio
import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from .docker_executor import DockerExecutor

app = FastAPI(title='VibeCode Executor Service')

# URL основного backend для callback
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000/api')

executor = DockerExecutor()


class TestCase(BaseModel):
    input: str
    output: str


class ExecuteRequest(BaseModel):
    execution_id: str
    language: str = Field(..., description='Язык программирования')
    files: dict[str, str] = Field(..., description='Файлы кода {path: content}')
    timeout: int = Field(default=30, ge=1, le=300)
    test_cases: list[TestCase] | None = Field(None, description='Тестовые случаи для проверки решения')


class ExecuteResponse(BaseModel):
    execution_id: str
    status: str = 'accepted'


@app.get('/health')
async def health():
    return {'status': 'ok', 'service': 'executor'}


@app.post('/execute', status_code=status.HTTP_202_ACCEPTED, response_model=ExecuteResponse)
async def execute_code(request: ExecuteRequest):
    """Принять задачу на выполнение (асинхронно)"""
    # Запускаем выполнение в фоне
    asyncio.create_task(run_execution(request))
    return ExecuteResponse(execution_id=request.execution_id, status='accepted')


async def run_execution(request: ExecuteRequest):
    """Выполнить код и отправить результат в backend"""
    started_at = datetime.now(timezone.utc)
    
    # Отправляем статус "running"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f'{BACKEND_URL}/executions/{request.execution_id}/callback',
                json={
                    'id': request.execution_id,
                    'status': 'running',
                    'result': None,
                    'error_message': None,
                    'started_at': started_at.isoformat(),
                    'completed_at': None,
                },
            )
    except Exception:  # noqa: BLE001
        pass  # Игнорируем ошибки callback
    
    try:
        # Выполняем код
        result = await executor.execute_code(
            language=request.language,
            files=request.files,
            timeout=request.timeout,
            test_cases=request.test_cases,
        )
        
        completed_at = datetime.now(timezone.utc)
        
        # Отправляем результат в backend
        callback_data = {
            'id': request.execution_id,
            'status': 'completed',
            'result': {
                'stdout': result['stdout'],
                'stderr': result['stderr'],
                'exit_code': result['exit_code'],
                'duration_ms': result['duration_ms'],
                'verdict': result.get('verdict'),
                'test_results': result.get('test_results'),
            },
            'error_message': None,
            'started_at': started_at.isoformat(),
            'completed_at': completed_at.isoformat(),
        }
        
    except Exception as exc:  # noqa: BLE001
        completed_at = datetime.now(timezone.utc)
        callback_data = {
            'id': request.execution_id,
            'status': 'failed',
            'result': None,
            'error_message': str(exc),
            'started_at': started_at.isoformat(),
            'completed_at': completed_at.isoformat(),
        }
    
    # Отправляем callback
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                f'{BACKEND_URL}/executions/{request.execution_id}/callback',
                json=callback_data,
            )
    except Exception as exc:  # noqa: BLE001
        # Логируем ошибку, но не падаем
        print(f'Failed to send callback: {exc}')  # noqa: T201


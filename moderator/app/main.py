"""Moderator Service - Микросервис для модерации заявок"""

import os
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='VibeCode Moderator Service')

# URL основного backend
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000/api')
MODERATOR_TOKEN = os.getenv('MODERATOR_TOKEN', 'moderator_secret_token')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class ModeratorAuth(BaseModel):
    """Авторизация модератора"""
    token: str = Field(..., description='Токен модератора')


class ApplicationDecision(BaseModel):
    """Решение по заявке"""
    application_id: str = Field(..., description='ID заявки')
    decision: str = Field(..., description='Решение: accepted или rejected')
    comment: str | None = Field(None, description='Комментарий (опционально)')


@app.get('/health')
async def health():
    return {'status': 'ok', 'service': 'moderator'}


@app.post('/auth')
async def authenticate(auth: ModeratorAuth):
    """Авторизация модератора"""
    if auth.token != MODERATOR_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid moderator token'
        )
    return {'authenticated': True}


@app.get('/applications')
async def list_applications(moderator_token: str):
    """Получить список заявок для модерации (статус algo_test_completed)"""
    if moderator_token != MODERATOR_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid moderator token'
        )
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f'{BACKEND_URL}/moderator/applications',
            headers={'X-Moderator-Token': MODERATOR_TOKEN}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        return response.json()


@app.get('/applications/{application_id}')
async def get_application(application_id: str, moderator_token: str):
    """Получить детальную информацию о заявке"""
    if moderator_token != MODERATOR_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid moderator token'
        )
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f'{BACKEND_URL}/moderator/applications/{application_id}',
            headers={'X-Moderator-Token': MODERATOR_TOKEN}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        return response.json()


@app.post('/applications/{application_id}/decide')
async def decide_application(
    application_id: str,
    decision: ApplicationDecision,
    moderator_token: str
):
    """Принять или отклонить заявку"""
    if moderator_token != MODERATOR_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid moderator token'
        )
    
    if decision.decision not in ['accepted', 'rejected']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Decision must be "accepted" or "rejected"'
        )
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f'{BACKEND_URL}/moderator/applications/{application_id}/decide',
            json=decision.model_dump(),
            headers={'X-Moderator-Token': MODERATOR_TOKEN}
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        return response.json()


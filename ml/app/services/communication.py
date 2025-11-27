from app.core.config import settings
from app.services.llm_client import llm_client
import json

class CommunicationEvaluator:
    """Оценщик коммуникативных навыков кандидата."""
    
    async def evaluate_explanation(self, problem_desc: str, user_explanation: str, code: str = None) -> dict:
        """Оценивает объяснение решения кандидатом.
        
        Args:
            problem_desc: Описание задачи
            user_explanation: Объяснение пользователя
            code: Код решения (опционально)
            
        Returns:
            dict: Оценка коммуникации и обратная связь
        """
        code_section = f"\n\nКод кандидата:\n```python\n{code}\n```" if code else ""
        
        prompt = f"""
        Ты интервьюер, оценивающий объяснение кандидата.
        
        Задача: {problem_desc}
        Объяснение кандидата: "{user_explanation}"{code_section}
        
        Оцени коммуникативные навыки по шкале от 0.0 до 1.0.
        Учитывай: ясность, корректность терминологии и логику изложения.
        {f"Также проверь, соответствует ли объяснение представленному коду." if code else ""}
        
        ВАЖНО: Верни ТОЛЬКО валидный JSON. Обратная связь должна быть НА РУССКОМ ЯЗЫКЕ.
        
        Формат JSON:
        {{
            "communication_score": float,
            "feedback": "string (на русском языке)"
        }}
        """
        
        return await llm_client.generate_json(
            model=settings.MODEL_AWQ,
            messages=[
                {"role": "system", "content": "Ты технический интервьюер. Всегда отвечай на русском языке."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
    async def generate_followup_question(self, problem_desc: str, code: str) -> str:
        """Генерирует дополнительный вопрос для интервью.
        
        Args:
            problem_desc: Описание задачи
            code: Код кандидата
            
        Returns:
            str: Дополнительный вопрос
        """
        prompt = f"""
        Кандидат решил следующую задачу:
        {problem_desc}
        
        Код:
        {code}
        
        Задай один проницательный дополнительный вопрос о временной сложности, граничных случаях или потенциальных оптимизациях.
        Вопрос должен быть НА РУССКОМ ЯЗЫКЕ.
        """
        return await llm_client.generate(
            model=settings.MODEL_AWQ, 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

communication_service = CommunicationEvaluator()

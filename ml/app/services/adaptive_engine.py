from typing import Literal
from app.models.schemas import AdaptiveLevelRequest, AdaptiveLevelResponse

class AdaptiveDifficultyEngine:
    """Адаптивный движок для определения следующего уровня сложности.
    
    Логика переходов:
    - Старт: всегда Medium
    - Medium пройден → Hard (если мало ошибок) или Medium (если 2+ плохих попыток)
    - Medium провален → Easy
    - Easy пройден → Medium
    - Easy провален → Easy
    - Hard пройден → Hard
    - Hard провален → Medium
    """
    
    def determine_next_level(self, request: AdaptiveLevelRequest) -> AdaptiveLevelResponse:
        """Определяет следующий уровень сложности на основе результатов.
        
        Args:
            request: Запрос с текущим уровнем, результатом и количеством плохих попыток
            
        Returns:
            AdaptiveLevelResponse: Следующий уровень и причина выбора
        """
        current = request.current_difficulty
        passed = request.is_passed
        bad_attempts = request.bad_attempts
        
        next_level = current  # По умолчанию оставляем текущий уровень
        reason = "Уровень сохранён."

        if current == "medium":
            if passed:
                if bad_attempts >= 2:
                    next_level = "medium"
                    reason = "Пройдено, но с множественными ошибками. Закрепляем Medium."
                else:
                    next_level = "hard"
                    reason = "Пройдено Medium успешно. Повышаем до Hard."
            else:
                next_level = "easy"
                reason = "Провал Medium. Понижаем до Easy для практики."
                
        elif current == "easy":
            if passed:
                next_level = "medium"
                reason = "Пройдено Easy. Повышаем до Medium."
            else:
                next_level = "easy"
                reason = "Провал Easy. Повторяем Easy."
                
        elif current == "hard":
            if passed:
                next_level = "hard"
                reason = "Пройдено Hard. Отлично! Сохраняем сложный уровень."
            else:
                next_level = "medium"
                reason = "Провал Hard. Понижаем до Medium."
                
        return AdaptiveLevelResponse(next_level=next_level, reason=reason)

adaptive_engine = AdaptiveDifficultyEngine()

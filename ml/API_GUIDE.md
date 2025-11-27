# Руководство по API ML сервиса VibeCode Jam

## Обзор

ML сервис предоставляет REST API для генерации задач, оценки решений, адаптивной сложности и анализа коммуникации.

**Базовый URL:** `http://localhost:8001/api/v1`

## Эндпоинты

### 1. Генерация задач

#### POST `/generate-task`
Генерирует алгоритмическую задачу на русском языке с использованием LLM.

**Запрос:**
```json
{
  "difficulty": "easy" | "medium" | "hard",
  "topic": "string (опционально)"
}
```

**Ответ:**
```json
{
  "title": "Название задачи",
  "description": "Подробное описание задачи",
  "input_format": "Формат входных данных",
  "output_format": "Формат выходных данных",
  "examples": [
    {
      "input": "пример входных данных",
      "output": "пример выходных данных"
    }
  ],
  "constraints": ["ограничение 1", "ограничение 2"],
  "difficulty": "easy",
  "hidden_tests": ["тест 1", "тест 2", ...]
}
```

**Пример:**
```bash
curl -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'
```

**Время выполнения:** 10-30 секунд (зависит от LLM)

---

#### POST `/generate-task-mock`
Mock эндпоинт для тестирования без LLM (мгновенный ответ).

**Запрос:** Аналогичен `/generate-task`

**Ответ:** Предопределенная задача "Найти максимальный элемент в массиве"

**Пример:**
```bash
curl -X POST "http://localhost:8001/api/v1/generate-task-mock" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'
```

---

### 2. Оценка решений

#### POST `/evaluate`
Оценивает код решения: запускает тесты и анализирует качество.

**Запрос:**
```json
{
  "code": "def solution():\n    pass",
  "task_difficulty": "easy" | "medium" | "hard",
  "task_description": "Описание задачи",
  "hidden_tests": ["тест 1", "тест 2"]
}
```

**Ответ:**
```json
{
  "tests_passed": 5,
  "total_tests": 5,
  "passed": true,
  "code_quality_score": 85,
  "feedback": "Отличное решение! Код читаемый и эффективный."
}
```

**Пример:**
```bash
curl -X POST "http://localhost:8001/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def max_element(arr):\n    return max(arr)",
    "task_difficulty": "easy",
    "task_description": "Найти максимальный элемент",
    "hidden_tests": ["1 2 3", "10 20 30"]
  }'
```

---

### 3. Адаптивный движок

#### POST `/adaptive-engine`
Определяет следующий уровень сложности на основе результатов.

**Запрос:**
```json
{
  "current_difficulty": "easy" | "medium" | "hard",
  "passed_tests": 5,
  "total_tests": 5,
  "time_taken_seconds": 120,
  "code_quality_score": 85
}
```

**Ответ:**
```json
{
  "next_difficulty": "medium",
  "reasoning": "Отличные результаты! Переходим на средний уровень."
}
```

**Пример:**
```bash
curl -X POST "http://localhost:8001/api/v1/adaptive-engine" \
  -H "Content-Type: application/json" \
  -d '{
    "current_difficulty": "easy",
    "passed_tests": 5,
    "total_tests": 5,
    "time_taken_seconds": 120,
    "code_quality_score": 85
  }'
```

---

### 4. Оценка коммуникации

#### POST `/communication/evaluate`
Оценивает качество объяснения решения кандидатом.

**Запрос:**
```json
{
  "problem_description": "Описание задачи",
  "user_explanation": "Я использовал цикл for для перебора элементов...",
  "code": "def solution():\n    pass" // опционально
}
```

**Ответ:**
```json
{
  "communication_score": 0.85,
  "feedback": "Хорошее объяснение. Упомянуты ключевые моменты алгоритма. Объяснение соответствует коду."
}
```

**Пример:**
```bash
curl -X POST "http://localhost:8001/api/v1/communication/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Найти максимальный элемент",
    "user_explanation": "Я использовал цикл for для перебора элементов массива и переменную для хранения максимума",
    "code": "def max_element(arr):\n    return max(arr)"
  }'
```

---

### 5. Подсчет баллов

#### POST `/score`
Рассчитывает итоговый балл на основе всех метрик.

**Запрос:**
```json
{
  "difficulty": "easy" | "medium" | "hard",
  "tests_passed": 8,
  "total_tests": 10,
  "time_taken_seconds": 300,
  "code_quality_score": 75,
  "communication_score": 80
}
```

**Ответ:**
```json
{
  "final_score": 92.4
}
```

**Формула расчета:**
- 40% - корректность (tests_passed / total_tests)
- 20% - качество кода (code_quality_score / 100)
- 20% - коммуникация (communication_score / 100)
- 20% - время (зависит от лимита по сложности)
- Множитель сложности: easy ×1.0, medium ×1.2, hard ×1.5
- Результат: 0-100 баллов

**Пример:**
```bash
curl -X POST "http://localhost:8001/api/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "medium",
    "tests_passed": 8,
    "total_tests": 10,
    "time_taken_seconds": 300,
    "code_quality_score": 75,
    "communication_score": 80
  }'
```

---

### 6. Анти-чит проверка

#### POST `/anti-cheat/check`
Проверяет код на плагиат и AI-генерацию.

**Запрос:**
```json
{
  "code": "def solution():\n    pass",
  "problem_description": "Описание задачи"
}
```

**Ответ:**
```json
{
  "is_suspicious": false,
  "confidence": 0.15,
  "reasons": []
}
```

**Пример:**
```bash
curl -X POST "http://localhost:8001/api/v1/anti-cheat/check" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def solution(arr):\n    return sorted(arr)",
    "problem_description": "Отсортировать массив"
  }'
```

---

## Служебные эндпоинты

### GET `/health`
Проверка работоспособности сервиса.

**Ответ:**
```json
{
  "status": "ok",
  "service": "ml"
}
```

**Пример:**
```bash
curl http://localhost:8001/health
```

---

## Swagger UI

Интерактивная документация API доступна по адресу:
```
http://localhost:8001/docs
```

Здесь вы можете:
- Просмотреть все эндпоинты
- Протестировать запросы через веб-интерфейс
- Посмотреть схемы данных

---

## Коды ошибок

- **200 OK** - Успешный запрос
- **422 Unprocessable Entity** - Ошибка валидации данных
- **500 Internal Server Error** - Ошибка сервера (обычно проблема с LLM)

**Формат ошибки:**
```json
{
  "detail": "Описание ошибки"
}
```

---

## Примеры использования

### Полный цикл собеседования

```bash
# 1. Генерация задачи
TASK=$(curl -s -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}')

echo "Задача: $(echo $TASK | jq -r '.title')"

# 2. Оценка решения
curl -X POST "http://localhost:8001/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d "{
    \"code\": \"def solution(): pass\",
    \"task_difficulty\": \"easy\",
    \"task_description\": \"$(echo $TASK | jq -r '.description')\",
    \"hidden_tests\": $(echo $TASK | jq '.hidden_tests')
  }"

# 3. Определение следующего уровня
curl -X POST "http://localhost:8001/api/v1/adaptive-engine" \
  -H "Content-Type: application/json" \
  -d '{
    "current_difficulty": "easy",
    "passed_tests": 5,
    "total_tests": 5,
    "time_taken_seconds": 180,
    "code_quality_score": 90
  }'
```

---

## Ограничения и рекомендации

1. **Timeout**: Генерация задач может занимать до 30 секунд
2. **Rate limiting**: Нет ограничений (для dev окружения)
3. **Язык**: Все задачи генерируются на русском языке
4. **LLM зависимость**: Требуется доступ к SciBox API

---

## Troubleshooting

Если возникают проблемы, смотрите [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

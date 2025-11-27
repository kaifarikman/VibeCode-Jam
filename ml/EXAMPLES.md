# Примеры использования ML API

## 1. Генерация задачи

### Запрос
```bash
curl -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "medium"
  }'
```

### Ответ
```json
{
  "title": "Найти первый уникальный символ",
  "description": "Дан массив символов. Найдите первый символ, который встречается только один раз.",
  "input_format": "Строка символов",
  "output_format": "Первый уникальный символ или -1",
  "examples": [
    {
      "input": "leetcode",
      "output": "l"
    },
    {
      "input": "loveleetcode",
      "output": "v"
    }
  ],
  "constraints": ["1 <= s.length <= 10^5"],
  "difficulty": "medium",
  "hidden_tests": ["aabbcc", "abcabc", "xyz"]
}
```

## 2. Оценка решения

### Запрос
```bash
curl -X POST "http://localhost:8001/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "s = input()\nfor char in s:\n    if s.count(char) == 1:\n        print(char)\n        break\nelse:\n    print(-1)",
    "task_difficulty": "medium",
    "task_description": "Найти первый уникальный символ",
    "hidden_tests": ["aabbcc", "abcabc", "xyz"]
  }'
```

### Ответ
```json
{
  "correctness_score": 1.0,
  "efficiency_score": 0.7,
  "clean_code_score": 0.9,
  "feedback": "Решение корректное, но можно оптимизировать используя хеш-таблицу для O(n) вместо O(n²)",
  "passed": true
}
```

## 3. Определение следующего уровня

### Запрос
```bash
curl -X POST "http://localhost:8001/api/v1/adaptive-engine" \
  -H "Content-Type: application/json" \
  -d '{
    "current_difficulty": "medium",
    "is_passed": true,
    "bad_attempts": 1,
    "total_time_seconds": 300
  }'
```

### Ответ
```json
{
  "next_difficulty": "hard",
  "reason": "Пройдено Medium успешно. Повышаем до Hard."
}
```

## 4. Оценка объяснения

### Запрос
```bash
curl -X POST "http://localhost:8001/api/v1/communication/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Найти первый уникальный символ",
    "user_explanation": "Я использовал цикл для перебора символов и метод count для подсчёта. Сложность O(n²), но код простой и понятный."
  }'
```

### Ответ
```json
{
  "communication_score": 0.85,
  "feedback": "Хорошее объяснение с указанием сложности. Можно было упомянуть возможные оптимизации."
}
```

## 5. Генерация follow-up вопроса

### Запрос
```bash
curl -X POST "http://localhost:8001/api/v1/communication/follow-up" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Найти первый уникальный символ",
    "code": "s = input()\nfor char in s:\n    if s.count(char) == 1:\n        print(char)\n        break"
  }'
```

### Ответ
```json
{
  "question": "Как можно оптимизировать ваше решение до O(n) временной сложности?"
}
```

## 6. Расчёт итогового балла

### Запрос
```bash
curl -X POST "http://localhost:8001/api/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "evaluation_result": {
      "correctness_score": 1.0,
      "efficiency_score": 0.7,
      "clean_code_score": 0.9,
      "feedback": "Хорошее решение",
      "passed": true
    },
    "communication_score": 0.85,
    "time_score": 0.8,
    "bad_attempts_count": 1
  }'
```

### Ответ
```json
{
  "final_score": 0.84
}
```

**Расчёт:**
```
0.45 × 1.0 (correctness) +
0.15 × 0.7 (efficiency) +
0.10 × 1.0 (reliability) +
0.10 × 0.85 (communication) +
0.10 × 0.8 (time) -
0.10 × 0.2 (bad_attempts: 1 × 0.2)
= 0.84
```

## 7. Проверка на плагиат

### Запрос
```bash
curl -X POST "http://localhost:8001/api/v1/anti-cheat/check" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def solution(arr):\n    # This is from StackOverflow\n    return max(arr)",
    "problem_description": "Найти максимальный элемент"
  }'
```

### Ответ
```json
{
  "is_suspicious": true,
  "confidence": 0.75,
  "reason": "Комментарий указывает на источник из StackOverflow. Код слишком простой для оценки плагиата."
}
```

## 8. Проверка здоровья сервиса

### Запрос
```bash
curl http://localhost:8001/health
```

### Ответ
```json
{
  "status": "ok",
  "service": "ml"
}
```

## Python примеры

### Полный цикл интервью

```python
import requests

BASE_URL = "http://localhost:8001/api/v1"

# 1. Генерация задачи (старт с Medium)
task_response = requests.post(f"{BASE_URL}/generate-task", json={
    "difficulty": "medium"
})
task = task_response.json()
print(f"Задача: {task['title']}")

# 2. Кандидат пишет код (симуляция)
candidate_code = """
s = input()
char_count = {}
for char in s:
    char_count[char] = char_count.get(char, 0) + 1
for char in s:
    if char_count[char] == 1:
        print(char)
        break
else:
    print(-1)
"""

# 3. Оценка решения
eval_response = requests.post(f"{BASE_URL}/evaluate", json={
    "code": candidate_code,
    "task_difficulty": task["difficulty"],
    "task_description": task["description"],
    "hidden_tests": task["hidden_tests"]
})
evaluation = eval_response.json()
print(f"Корректность: {evaluation['correctness_score']}")
print(f"Пройдено: {evaluation['passed']}")

# 4. Оценка объяснения
comm_response = requests.post(f"{BASE_URL}/communication/evaluate", json={
    "problem_description": task["description"],
    "user_explanation": "Я использовал хеш-таблицу для подсчёта частоты символов за O(n)"
})
communication = comm_response.json()
print(f"Коммуникация: {communication['communication_score']}")

# 5. Расчёт итогового балла
score_response = requests.post(f"{BASE_URL}/score", json={
    "evaluation_result": evaluation,
    "communication_score": communication["communication_score"],
    "time_score": 0.9,
    "bad_attempts_count": 0
})
final_score = score_response.json()
print(f"Итоговый балл: {final_score['final_score']}")

# 6. Определение следующего уровня
next_level_response = requests.post(f"{BASE_URL}/adaptive-engine", json={
    "current_difficulty": "medium",
    "is_passed": evaluation["passed"],
    "bad_attempts": 0
})
next_level = next_level_response.json()
print(f"Следующий уровень: {next_level['next_difficulty']}")
print(f"Причина: {next_level['reason']}")
```

## Swagger UI

Для интерактивного тестирования API откройте:
```
http://localhost:8001/docs
```

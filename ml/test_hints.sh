#!/bin/bash

echo "=== Тестирование системы подсказок ==="
echo ""

echo "1. Генерация задачи с подсказками (easy):"
TASK=$(curl -s -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}')

echo "Название задачи:"
echo "$TASK" | jq -r '.title'

echo ""
echo "Подсказки:"
echo "$TASK" | jq '.hints'

echo ""
echo "2. Расчет баллов БЕЗ подсказок:"
curl -s -X POST "http://localhost:8001/api/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "medium",
    "tests_passed": 8,
    "total_tests": 10,
    "time_taken_seconds": 300,
    "code_quality_score": 75,
    "communication_score": 80,
    "hints_used": []
  }' | jq .

echo ""
echo "3. Расчет баллов С ОДНОЙ поверхностной подсказкой (-5 баллов):"
curl -s -X POST "http://localhost:8001/api/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "medium",
    "tests_passed": 8,
    "total_tests": 10,
    "time_taken_seconds": 300,
    "code_quality_score": 75,
    "communication_score": 80,
    "hints_used": ["surface"]
  }' | jq .

echo ""
echo "4. Расчет баллов СО ВСЕМИ подсказками (-50 баллов):"
curl -s -X POST "http://localhost:8001/api/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "medium",
    "tests_passed": 8,
    "total_tests": 10,
    "time_taken_seconds": 300,
    "code_quality_score": 75,
    "communication_score": 80,
    "hints_used": ["surface", "medium", "deep"]
  }' | jq .

echo ""
echo "=== Тестирование завершено ==="

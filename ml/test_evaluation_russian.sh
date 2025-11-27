#!/bin/bash

echo "=== Тестирование оценки решений на русском языке ==="
echo ""

echo "1. Оценка простого решения (max element):"
curl -s -X POST "http://localhost:8001/api/v1/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def max_element(arr):\n    return max(arr)",
    "task_difficulty": "easy",
    "task_description": "Найти максимальный элемент в массиве",
    "hidden_tests": ["1 2 3 4 5", "10 20 30"]
  }' | jq -r '.feedback'

echo ""
echo "2. Оценка коммуникации (с кодом):"
curl -s -X POST "http://localhost:8001/api/v1/communication/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "Найти максимальный элемент в массиве",
    "user_explanation": "Я использовал цикл for для перебора всех элементов массива и переменную max_val для хранения максимального значения",
    "code": "def max_element(arr):\n    max_val = arr[0]\n    for x in arr:\n        if x > max_val:\n            max_val = x\n    return max_val"
  }' | jq -r '.communication_score, .feedback'

echo ""
echo "=== Тестирование завершено ==="

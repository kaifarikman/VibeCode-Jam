#!/bin/bash

echo "=== Тестирование анти-чит проверки на русском языке ==="
echo ""

echo "1. Проверка честного решения:"
curl -s -X POST "http://localhost:8001/api/v1/anti-cheat/check" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def max_element(arr):\n    max_val = arr[0]\n    for x in arr:\n        if x > max_val:\n            max_val = x\n    return max_val",
    "problem_description": "Найти максимальный элемент в массиве"
  }' | jq .

echo ""
echo "2. Проверка подозрительного кода (использует встроенную функцию):"
curl -s -X POST "http://localhost:8001/api/v1/anti-cheat/check" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def solution(arr):\n    # This is a standard solution from tutorial\n    return max(arr)  # Using built-in max function",
    "problem_description": "Найти максимальный элемент в массиве без использования встроенных функций"
  }' | jq .

echo ""
echo "=== Тестирование завершено ==="

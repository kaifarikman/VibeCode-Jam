#!/bin/bash

echo "=== Тестирование генерации задач на русском языке ==="
echo ""

echo "1. EASY задача:"
curl -s -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}' | jq -r '.title, .difficulty'

echo ""
echo "2. MEDIUM задача:"
curl -s -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "medium"}' | jq -r '.title, .difficulty'

echo ""
echo "3. HARD задача:"
curl -s -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "hard"}' | jq -r '.title, .difficulty'

echo ""
echo "=== Тестирование завершено ==="

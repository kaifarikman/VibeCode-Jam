#!/bin/bash

echo "=== Тестирование подсчета баллов ==="
echo ""

echo "1. Medium задача (8/10 тестов, 300 сек):"
curl -s -X POST "http://localhost:8001/api/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "medium",
    "tests_passed": 8,
    "total_tests": 10,
    "time_taken_seconds": 300,
    "code_quality_score": 75,
    "communication_score": 80
  }' | jq .

echo ""
echo "2. Easy задача (идеальное решение):"
curl -s -X POST "http://localhost:8001/api/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "easy",
    "tests_passed": 5,
    "total_tests": 5,
    "time_taken_seconds": 120,
    "code_quality_score": 90,
    "communication_score": 85
  }' | jq .

echo ""
echo "3. Hard задача (хорошее решение):"
curl -s -X POST "http://localhost:8001/api/v1/score" \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "hard",
    "tests_passed": 9,
    "total_tests": 10,
    "time_taken_seconds": 600,
    "code_quality_score": 80,
    "communication_score": 75
  }' | jq .

echo ""
echo "=== Тестирование завершено ==="

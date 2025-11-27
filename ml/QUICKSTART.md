# Быстрый старт ML сервиса

## Установка

```bash
cd ml
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn app.main:app --reload --port 8001
```

Сервис будет доступен по адресу: `http://localhost:8001`

## Документация API

После запуска откройте в браузере:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

## Основные эндпоинты

- `POST /api/v1/generate-task` - Генерация задачи
- `POST /api/v1/evaluate` - Оценка решения
- `POST /api/v1/adaptive-engine` - Определение следующего уровня
- `POST /api/v1/communication/evaluate` - Оценка объяснения
- `POST /api/v1/score` - Расчёт итогового балла
- `POST /api/v1/anti-cheat/check` - Проверка на плагиат

## Проверка работоспособности

```bash
# Проверка health эндпоинта
curl http://localhost:8001/health
# Ответ: {"status":"ok","service":"ml"}

# Тестирование генерации задачи (требует LLM API)
curl -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'

# Тестирование mock эндпоинта (без LLM)
curl -X POST "http://localhost:8001/api/v1/generate-task-mock" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'
```

## Конфигурация LLM API

Создайте файл `.env` в директории `ml/`:

```bash
SCIBOX_API_KEY=sk-c7K8ClMXslvPl6SRw2P9Ig
SCIBOX_API_BASE=https://llm.t1v.scibox.tech/v1
```

**Важно:** После изменения `.env` необходимо перезапустить сервер.

## Тестирование генерации на русском языке

Запустите тестовый скрипт:
```bash
./test_russian.sh
```

Или вручную:
```bash
# Easy задача
curl -s -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}' | jq -r '.title, .description'

# Medium задача  
curl -s -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "medium"}' | jq -r '.title, .description'

# Hard задача
curl -s -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "hard"}' | jq -r '.title, .description'
```

**Примеры сгенерированных задач:**
- Easy: "Найти максимальный элемент", "Подсчёт чётных чисел"
- Medium: "Наибольший общий префикс", "Первый уникальный символ"
- Hard: "Реализация QuickSort", "Сортировка связного списка"

## Troubleshooting

Если возникают проблемы, смотрите [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

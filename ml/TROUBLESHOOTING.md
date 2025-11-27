# Troubleshooting Guide

## Проблема: "Ошибка LLM клиента" при вызове /api/v1/generate-task

### Описание проблемы
При выполнении запроса:
```bash
curl -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'
```

Возвращается ошибка:
```json
{"detail":"Ошибка LLM клиента: "}
```

### Причина
Неправильный URL API или отсутствие доступа к LLM сервису.

### Решение

#### Вариант 1: Использование публичного API SciBox (РЕКОМЕНДУЕТСЯ)
1. Обновите файл `.env` с правильными настройками:
   ```bash
   SCIBOX_API_KEY=sk-c7K8ClMXslvPl6SRw2P9Ig
   SCIBOX_API_BASE=https://llm.t1v.scibox.tech/v1
   ```
2. Перезапустите сервер:
   ```bash
   pkill -f "uvicorn app.main:app"
   cd ml && source venv/bin/activate && uvicorn app.main:app --reload --port 8001
   ```
3. Проверьте доступность API:
   ```bash
   curl -H "Authorization: Bearer sk-c7K8ClMXslvPl6SRw2P9Ig" https://llm.t1v.scibox.tech/v1/models
   ```

#### Вариант 2: Использование mock эндпоинта (для тестирования)
Используйте mock эндпоинт, который не требует внешнего LLM:
```bash
curl -X POST "http://localhost:8001/api/v1/generate-task-mock" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'
```

### Улучшения в коде
1. **Улучшена обработка ошибок** в `llm_client.py`:
   - Добавлены информативные сообщения об ошибках
   - Указание на необходимость VPN подключения
   - Обработка различных типов ошибок (ConnectError, HTTPStatusError, TimeoutException)

2. **Добавлен mock эндпоинт** `/api/v1/generate-task-mock` для тестирования без зависимости от внешнего API

### Проверка работоспособности
```bash
# Проверка health эндпоинта
curl http://localhost:8001/health

# Тестирование mock эндпоинта
curl -X POST "http://localhost:8001/api/v1/generate-task-mock" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'
```

### Конфигурация
Настройки API находятся в `app/core/config.py` и `.env`:
- `SCIBOX_API_KEY`: API ключ для SciBox (sk-c7K8ClMXslvPl6SRw2P9Ig)
- `SCIBOX_API_BASE`: Базовый URL API (https://llm.t1v.scibox.tech/v1)
- `MODEL_AWQ`: Модель для генерации задач (qwen3-32b-awq)
- `MODEL_CODER`: Модель для генерации тестов (qwen3-coder-30b-a3b-instruct-fp8)

**Важно:** Файл `.env` переопределяет настройки из `config.py`. После изменения `.env` необходимо перезапустить сервер.

### Доступные модели
Список доступных моделей можно получить командой:
```bash
curl -H "Authorization: Bearer sk-c7K8ClMXslvPl6SRw2P9Ig" https://llm.t1v.scibox.tech/v1/models
```

Доступные модели:
- `bge-m3` - Embedding модель
- `qwen3-coder-30b-a3b-instruct-fp8` - Специализированная модель для кода
- `qwen3-32b-awq` - Универсальная модель

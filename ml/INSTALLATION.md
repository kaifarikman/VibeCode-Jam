# 📦 Пошаговая инструкция по установке и запуску ML сервиса

## Требования

- **Python**: версия 3.11 или выше
- **pip**: менеджер пакетов Python
- **Интернет**: для установки зависимостей и обращения к LLM API

## Шаг 1: Проверка версии Python

Откройте терминал и выполните:

```bash
python3 --version
```

Должно быть **Python 3.11** или выше. Если версия ниже, обновите Python.

## Шаг 2: Переход в директорию проекта

```bash
cd /Users/glebgrigorev/Desktop/programming/VibeCode-Jam/ml
```

Или если вы находитесь в корне проекта:

```bash
cd ml
```

## Шаг 3: Создание виртуального окружения (рекомендуется)

Создайте виртуальное окружение для изоляции зависимостей:

```bash
python3 -m venv venv
```

Активируйте виртуальное окружение:

**На macOS/Linux:**
```bash
source venv/bin/activate
```

**На Windows:**
```bash
venv\Scripts\activate
```

После активации в начале строки терминала появится `(venv)`.

## Шаг 4: Установка зависимостей

Установите все необходимые пакеты из `requirements.txt`:

```bash
pip install -r requirements.txt
```

Это установит:
- `fastapi==0.115.5` - веб-фреймворк
- `uvicorn[standard]==0.32.1` - ASGI сервер
- `httpx==0.27.0` - HTTP клиент для запросов к LLM
- `pydantic-settings==2.7.1` - управление настройками

**Ожидаемый вывод:**
```
Successfully installed fastapi-0.115.5 uvicorn-0.32.1 httpx-0.27.0 pydantic-settings-2.7.1 ...
```

## Шаг 5: Проверка установки зависимостей

Проверьте, что все пакеты установлены корректно:

```bash
pip list | grep -E "fastapi|uvicorn|httpx|pydantic"
```

Должны отобразиться все четыре пакета с версиями.

## Шаг 6: Проверка файла .env

Убедитесь, что файл `.env` существует и содержит API ключ:

```bash
cat .env
```

Должно быть:
```
SCIBOX_API_KEY=sk-c7K8ClMXslvPl6SRw2P9Ig
SCIBOX_API_BASE=https://llm.ml-dev.scibox.tech/openai/v1
```

Если файла нет, создайте его:

```bash
cp env.example .env
```

## Шаг 7: Проверка структуры проекта

Убедитесь, что все файлы на месте:

```bash
ls -la app/
```

Должны быть папки:
- `core/` - конфигурация
- `models/` - схемы данных
- `routes/` - API эндпоинты
- `services/` - бизнес-логика
- `main.py` - точка входа

## Шаг 8: Запуск сервера

Запустите ML сервис:

```bash
uvicorn app.main:app --reload --port 8001
```

**Параметры:**
- `app.main:app` - путь к FastAPI приложению
- `--reload` - автоматическая перезагрузка при изменении кода
- `--port 8001` - порт для сервиса (8001, чтобы не конфликтовать с backend на 8000)

**Ожидаемый вывод:**
```
INFO:     Will watch for changes in these directories: ['/Users/glebgrigorev/Desktop/programming/VibeCode-Jam/ml']
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Шаг 9: Проверка работоспособности

Откройте **новый терминал** (не закрывая сервер) и выполните:

```bash
curl http://localhost:8001/health
```

**Ожидаемый ответ:**
```json
{"status":"ok","service":"ml"}
```

Если получили этот ответ - сервис работает! ✅

## Шаг 10: Открытие документации API

Откройте в браузере:

**Swagger UI (интерактивная документация):**
```
http://localhost:8001/docs
```

**ReDoc (альтернативная документация):**
```
http://localhost:8001/redoc
```

В Swagger UI вы можете протестировать все эндпоинты прямо в браузере.

## Шаг 11: Тестирование эндпоинтов

### Тест 1: Генерация задачи

```bash
curl -X POST "http://localhost:8001/api/v1/generate-task" \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}'
```

Должен вернуться JSON с задачей.

### Тест 2: Проверка адаптивного движка

```bash
curl -X POST "http://localhost:8001/api/v1/adaptive-engine" \
  -H "Content-Type: application/json" \
  -d '{
    "current_difficulty": "medium",
    "is_passed": true,
    "bad_attempts": 0
  }'
```

Должен вернуться следующий уровень сложности.

## 🎉 Готово!

ML сервис успешно запущен и готов к работе!

---

## 🔧 Устранение неполадок

### Проблема: `ModuleNotFoundError: No module named 'pydantic_settings'`

**Решение:**
```bash
pip install pydantic-settings==2.7.1
```

### Проблема: `Address already in use`

Порт 8001 занят другим процессом.

**Решение 1:** Используйте другой порт:
```bash
uvicorn app.main:app --reload --port 8002
```

**Решение 2:** Найдите и остановите процесс на порту 8001:
```bash
lsof -ti:8001 | xargs kill -9
```

### Проблема: `SCIBOX_API_KEY not found`

Файл `.env` не найден или пустой.

**Решение:**
```bash
echo "SCIBOX_API_KEY=sk-c7K8ClMXslvPl6SRw2P9Ig" > .env
echo "SCIBOX_API_BASE=https://llm.ml-dev.scibox.tech/openai/v1" >> .env
```

### Проблема: `HTTP error: 401 - Unauthorized`

Неверный API ключ.

**Решение:** Проверьте, что в `.env` указан правильный ключ:
```bash
cat .env | grep SCIBOX_API_KEY
```

### Проблема: `Connection refused` при запросах к LLM

API сервис недоступен.

**Решение:** Проверьте доступность API:
```bash
curl -I https://llm.ml-dev.scibox.tech/openai/v1/models
```

---

## 🛑 Остановка сервера

Для остановки сервера нажмите в терминале:
```
CTRL + C
```

Для деактивации виртуального окружения:
```bash
deactivate
```

---

## 🚀 Запуск в production режиме

Для production используйте без `--reload`:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
```

**Параметры:**
- `--host 0.0.0.0` - доступ извне
- `--workers 4` - количество worker процессов

---

## 📊 Мониторинг логов

Логи выводятся в консоль. Для сохранения в файл:

```bash
uvicorn app.main:app --reload --port 8001 > ml_service.log 2>&1 &
```

Просмотр логов в реальном времени:
```bash
tail -f ml_service.log
```

---

## 🔄 Автоматический запуск при старте системы (опционально)

### На macOS (через launchd):

Создайте файл `~/Library/LaunchAgents/com.vibecode.ml.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.vibecode.ml</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/glebgrigorev/Desktop/programming/VibeCode-Jam/ml/venv/bin/uvicorn</string>
        <string>app.main:app</string>
        <string>--port</string>
        <string>8001</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/glebgrigorev/Desktop/programming/VibeCode-Jam/ml</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Загрузите сервис:
```bash
launchctl load ~/Library/LaunchAgents/com.vibecode.ml.plist
```

### На Linux (через systemd):

Создайте файл `/etc/systemd/system/vibecode-ml.service`:

```ini
[Unit]
Description=VibeCode ML Service
After=network.target

[Service]
Type=simple
User=glebgrigorev
WorkingDirectory=/Users/glebgrigorev/Desktop/programming/VibeCode-Jam/ml
ExecStart=/Users/glebgrigorev/Desktop/programming/VibeCode-Jam/ml/venv/bin/uvicorn app.main:app --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Запустите сервис:
```bash
sudo systemctl enable vibecode-ml
sudo systemctl start vibecode-ml
```

---

## 📚 Дополнительные ресурсы

- **README.md** - Полная документация архитектуры
- **QUICKSTART.md** - Краткий гайд по запуску
- **EXAMPLES.md** - Примеры использования API
- **SUMMARY.md** - Сводка функционала

---

## ✅ Чеклист успешной установки

- [ ] Python 3.11+ установлен
- [ ] Виртуальное окружение создано и активировано
- [ ] Все зависимости установлены (`pip list`)
- [ ] Файл `.env` существует с API ключом
- [ ] Сервер запускается без ошибок
- [ ] Health check возвращает `{"status":"ok"}`
- [ ] Swagger UI открывается в браузере
- [ ] Тестовый запрос к `/generate-task` работает

Если все пункты отмечены - установка прошла успешно! 🎉

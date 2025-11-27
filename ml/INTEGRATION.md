# Интеграция ML микросервиса с основным проектом

## 📋 Обзор

ML микросервис предоставляет AI-функции для платформы VibeCode Jam:
- 🎯 Генерация задач на русском языке
- 💡 Система подсказок трех уровней (-5, -15, -30 баллов)
- ✅ Оценка кода и коммуникации
- 🎯 Расчет финального балла
- 🛡️ Анти-чит проверка

**Базовый URL:** `http://localhost:8001/api/v1`

---

## 🌐 Ключевые эндпоинты

### 1. Генерация задачи с подсказками
**POST** `/generate-task`

```javascript
const response = await axios.post('http://localhost:8001/api/v1/generate-task', {
  difficulty: 'medium'
});

// Ответ включает:
const task = {
  title: "Название задачи",
  description: "Описание на русском",
  examples: [{input: "...", output: "..."}],
  hidden_tests: ["..."],  // Для проверки
  hints: [  // 💡 ТРИ УРОВНЯ ПОДСКАЗОК
    {level: "surface", content: "...", penalty: 5.0},
    {level: "medium", content: "...", penalty: 15.0},
    {level: "deep", content: "...", penalty: 30.0}
  ]
};
```

**❗ Важно:** НЕ отправляйте `hints` и `hidden_tests` фронтенду!

---

### 2. Запрос подсказки (в бэкенде)

```javascript
app.post('/api/interviews/:id/hints/:level', async (req, res) => {
  const interview = await Interview.findById(req.params.id).populate('task');
  
  // Проверьте, не использована ли уже
  const alreadyUsed = interview.hintsUsed.some(h => h.level === req.params.level);
  if (alreadyUsed) {
    return res.status(400).json({error: 'Подсказка уже использована'});
  }
  
  // Найдите подсказку в задаче
  const hint = interview.task.hints.find(h => h.level === req.params.level);
  
  // Сохраните использование
  interview.hintsUsed.push({
    level: hint.level,
    timestamp: new Date(),
    penalty: hint.penalty
  });
  await interview.save();
  
  res.json({
    content: hint.content,
    penalty: hint.penalty,
    remainingHints: 3 - interview.hintsUsed.length
  });
});
```

---

### 3. Оценка решения
**POST** `/evaluate`

```javascript
const evaluation = await axios.post('http://localhost:8001/api/v1/evaluate', {
  code: submission.code,
  task_difficulty: task.difficulty,
  task_description: task.description,
  hidden_tests: task.hidden_tests
});

// Ответ:
{
  correctness_score: 0.9,
  efficiency_score: 0.85,
  clean_code_score: 0.95,
  feedback: "Обратная связь на русском",
  passed: true
}
```

---

### 4. Расчет финального балла С УЧЕТОМ ПОДСКАЗОК
**POST** `/score`

```javascript
// Соберите использованные подсказки
const hintsUsed = interview.hintsUsed.map(h => h.level);
// Пример: ["surface", "medium"]

const scoreResponse = await axios.post('http://localhost:8001/api/v1/score', {
  difficulty: 'medium',
  tests_passed: 8,
  total_tests: 10,
  time_taken_seconds: 300,
  code_quality_score: 75,
  communication_score: 80,
  hints_used: hintsUsed  // 💡 ВАЖНО!
});

// Ответ:
{
  final_score: 72.4  // 92.4 - 5 - 15 = 72.4
}
```

**Формула:**
```
Базовый балл = (
  40% × корректность +
  20% × качество кода +
  20% × коммуникация +
  20% × время
) × множитель_сложности × 100

Финальный балл = Базовый - Штрафы за подсказки
```

---

## 📊 Модели данных

### Task (Задача)
```javascript
const taskSchema = new Schema({
  title: String,
  description: String,
  difficulty: {type: String, enum: ['easy', 'medium', 'hard']},
  examples: [{input: String, output: String}],
  hidden_tests: [String],
  hints: [{
    level: {type: String, enum: ['surface', 'medium', 'deep']},
    content: String,
    penalty: Number
  }]
});
```

### Interview (Сессия)
```javascript
const interviewSchema = new Schema({
  candidateId: ObjectId,
  taskId: ObjectId,
  startTime: Date,
  hintsUsed: [{
    level: String,
    timestamp: Date,
    penalty: Number
  }],
  finalScore: Number
});
```

---

## 🔄 Типичный flow

### 1. Начало интервью
```javascript
// Сгенерируйте задачу
const taskData = await axios.post('http://localhost:8001/api/v1/generate-task', {
  difficulty: 'medium'
});

// Сохраните в БД (с подсказками)
const task = await Task.create(taskData.data);

// Отправьте фронтенду БЕЗ подсказок
res.json({
  task: {
    title: task.title,
    description: task.description,
    examples: task.examples
    // НЕ отправляйте hints и hidden_tests!
  }
});
```

### 2. Завершение интервью
```javascript
// Соберите данные
const hintsUsed = interview.hintsUsed.map(h => h.level);
const timeSpent = (interview.endTime - interview.startTime) / 1000;

// Рассчитайте финальный балл
const scoreResponse = await axios.post('http://localhost:8001/api/v1/score', {
  difficulty: task.difficulty,
  tests_passed: lastSubmission.evaluation.passed ? 10 : 8,
  total_tests: 10,
  time_taken_seconds: timeSpent,
  code_quality_score: lastSubmission.evaluation.clean_code_score * 100,
  communication_score: interview.communicationScore || 80,
  hints_used: hintsUsed
});

interview.finalScore = scoreResponse.data.final_score;
await interview.save();
```

---

## 💡 Штрафы за подсказки

| Подсказки | Штраф | Пример балла |
|-----------|-------|----------------|
| Нет | 0 | 92.4 |
| surface | -5 | 87.4 |
| surface + medium | -20 | 72.4 |
| Все три | -50 | 42.4 |

---

## 🔧 Настройка

### ML сервис (.env)
```bash
SCIBOX_API_KEY=your_api_key
SCIBOX_API_BASE=https://api.scibox.com/v1
```

### Бэкенд (.env)
```bash
ML_SERVICE_URL=http://localhost:8001/api/v1
ML_SERVICE_TIMEOUT=30000
```

---

## 🧪 Тестирование

```bash
# Проверьте ML сервис
curl http://localhost:8001/health

# Сгенерируйте задачу
curl -X POST http://localhost:8001/api/v1/generate-task \
  -H "Content-Type: application/json" \
  -d '{"difficulty": "easy"}' | jq '.hints'

# Рассчитайте балл с подсказками
curl -X POST http://localhost:8001/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{
    "difficulty": "medium",
    "tests_passed": 8,
    "total_tests": 10,
    "time_taken_seconds": 300,
    "code_quality_score": 75,
    "communication_score": 80,
    "hints_used": ["surface", "medium"]
  }'
```

---

## 📚 Документация

- **API_GUIDE.md** - Подробное описание всех эндпоинтов
- **HINTS_GUIDE.md** - Руководство по системе подсказок
- **SWAGGER_TESTING.md** - Тестирование через Swagger UI
- **Swagger UI:** http://localhost:8001/docs

---

## ❗ Важные моменты

1. **НЕ отправляйте подсказки фронтенду** при создании задачи
2. **Храните подсказки в БД** вместе с задачей
3. **Отслеживайте использование** каждой подсказки
4. **Передавайте `hints_used`** при расчете финального балла
5. **Все тексты на русском** - задачи, подсказки, обратная связь
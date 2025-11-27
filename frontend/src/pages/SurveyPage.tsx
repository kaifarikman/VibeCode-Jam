import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { submitAnswer } from '../modules/questions/api'
import { getSurveyQuestions, getRandomTasks, getMyApplications, updateApplicationStatus } from '../modules/vacancies/api'
import type { Question } from '../modules/questions/types'
import '../App.css'
import './SurveyPage.css'

export function SurveyPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const vacancyId = searchParams.get('vacancy_id') || ''

  const [questions, setQuestions] = useState<Question[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = window.localStorage.getItem('vibecode_token')
    if (!token) {
      navigate('/')
      return
    }
    if (!vacancyId) {
      navigate('/home')
      return
    }
    void checkAndLoadSurvey(token)
  }, [vacancyId, navigate])
  
  const checkAndLoadSurvey = async (token: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // Проверяем статус заявки
      const applications = await getMyApplications(token)
      const application = applications.find(app => app.vacancy_id === vacancyId)
      
      if (application && application.status !== 'pending') {
        // Опрос уже пройден, перенаправляем на страницу деталей вакансии
        setError('Вы уже прошли опрос по этой вакансии. Повторное прохождение невозможно.')
        setTimeout(() => {
          navigate(`/vacancy/${vacancyId}`)
        }, 2000)
        return
      }
      
      // Дополнительная проверка: если статус survey_completed или выше, блокируем
      if (application && ['survey_completed', 'algo_test_completed', 'under_review', 'accepted', 'rejected'].includes(application.status)) {
        setError('Опрос уже завершен. Повторное прохождение невозможно.')
        setTimeout(() => {
          navigate(`/vacancy/${vacancyId}`)
        }, 2000)
        return
      }
      
      // Загружаем вопросы для опроса
      await loadQuestions(token)
    } catch (err) {
      console.error('Error in checkAndLoadSurvey:', err)
      const errorMessage = err instanceof Error ? err.message : 'Ошибка загрузки данных'
      setError(errorMessage)
      // Если ошибка критическая, можно перенаправить на страницу вакансии
      if (errorMessage.includes('не найдена') || errorMessage.includes('404')) {
        setTimeout(() => {
          navigate(`/vacancy/${vacancyId}`)
        }, 2000)
      }
    } finally {
      setLoading(false)
    }
  }

  const loadQuestions = async (token: string) => {
    try {
      setLoading(true)
      setError(null)
      
      // Получаем случайные вопросы для опроса (до 10)
      const data = await getSurveyQuestions(token, vacancyId)
      
      if (!data || data.length === 0) {
        setError('Нет вопросов для этой вакансии')
        return
      }
      
      setQuestions(data)
    } catch (err) {
      console.error('Error in loadQuestions:', err)
      const errorMessage = err instanceof Error ? err.message : 'Ошибка загрузки вопросов'
      setError(errorMessage)
      
      // Если нет вопросов, перенаправляем обратно
      if (errorMessage.includes('Нет вопросов') || errorMessage.includes('400')) {
        setTimeout(() => {
          navigate(`/vacancy/${vacancyId}`)
        }, 2000)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleAnswerChange = (questionId: string, value: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: value }))
  }

  const handleNext = async () => {
    const token = window.localStorage.getItem('vibecode_token')
    if (!token) return

    const currentQuestion = questions[currentQuestionIndex]
    const answerText = answers[currentQuestion.id]

    if (!answerText?.trim()) {
      setError('Пожалуйста, ответьте на вопрос')
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      await submitAnswer(token, currentQuestion.id, {
        question_id: currentQuestion.id,
        text: answerText,
      })

      // Проверяем, это последний вопрос или нет
      const isLastQuestion = currentQuestionIndex >= questions.length - 1
      
      if (isLastQuestion) {
        // Все вопросы отвечены, переходим к завершению опроса
        await handleCompleteSurvey(token)
      } else {
        // Переходим к следующему вопросу
        setCurrentQuestionIndex(currentQuestionIndex + 1)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка сохранения ответа')
    } finally {
      setSubmitting(false)
    }
  }

  const handleCompleteSurvey = async (token: string) => {
    try {
      setSubmitting(true)
      
      // Находим заявку пользователя на эту вакансию
      const applications = await getMyApplications(token)
      const application = applications.find(app => app.vacancy_id === vacancyId)
      
      if (application) {
        // Обновляем статус заявки на "survey_completed"
        await updateApplicationStatus(token, application.id, 'survey_completed')
      }
      
      // Заглушка для ML оценки
      const mlScore = await evaluateAnswersWithML(token, vacancyId, answers)
      
      // Переходим на страницу поздравления
      navigate(`/survey-complete?vacancy_id=${vacancyId}&ml_score=${mlScore}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка завершения опроса')
      setSubmitting(false)
    }
  }

  const evaluateAnswersWithML = async (
    token: string,
    vacancyId: string,
    answers: Record<string, string>,
  ): Promise<number> => {
    // Заглушка ML оценки - возвращает случайный score от 0 до 100
    // TODO: Заменить на реальный ML сервис
    await new Promise((resolve) => setTimeout(resolve, 1000)) // Имитация задержки
    return Math.floor(Math.random() * 100)
  }

  const renderQuestionInput = (question: Question) => {
    const answerValue = answers[question.id] || ''

    switch (question.question_type) {
      case 'choice':
        try {
          const options = question.options ? JSON.parse(question.options) : []
          return (
            <div className="choice-options">
              {options.map((option: string, index: number) => (
                <label key={index} className="choice-option">
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={option}
                    checked={answerValue === option}
                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          )
        } catch {
          return (
            <textarea
              value={answerValue}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              placeholder="Введите ваш ответ..."
              rows={4}
              required
            />
          )
        }

      case 'multiple_choice':
        try {
          const options = question.options ? JSON.parse(question.options) : []
          const selectedValues = answerValue ? answerValue.split(',') : []
          return (
            <div className="choice-options">
              {options.map((option: string, index: number) => (
                <label key={index} className="choice-option">
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(option)}
                    onChange={(e) => {
                      const newValues = e.target.checked
                        ? [...selectedValues, option]
                        : selectedValues.filter((v) => v !== option)
                      handleAnswerChange(question.id, newValues.join(','))
                    }}
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          )
        } catch {
          return (
            <textarea
              value={answerValue}
              onChange={(e) => handleAnswerChange(question.id, e.target.value)}
              placeholder="Введите ваш ответ..."
              rows={4}
              required
            />
          )
        }

      default: // text
        return (
          <textarea
            value={answerValue}
            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
            placeholder="Введите ваш ответ..."
            rows={6}
            required
          />
        )
    }
  }

  if (loading) {
    return (
      <div className="survey-page">
        <div className="loading">Загрузка вопросов...</div>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="survey-page">
        <div className="no-questions">
          <p>Вопросы не найдены</p>
          <button type="button" className="back-btn" onClick={() => navigate('/home')}>
            Вернуться
          </button>
        </div>
      </div>
    )
  }

  const currentQuestion = questions[currentQuestionIndex]

  return (
    <div className="survey-page">
      <header className="survey-header">
        <div className="logo">FUTURECAREER</div>
        <button
          type="button"
          className="back-btn"
          onClick={() => navigate('/vacancies')}
          disabled={submitting}
        >
          ← Назад
        </button>
      </header>

      <section className="survey-content">
        <div className="survey-container">
          <div className="survey-progress">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${((currentQuestionIndex + 1) / questions.length) * 100}%`,
                }}
              />
            </div>
            <p className="progress-text">
              Вопрос {currentQuestionIndex + 1} из {questions.length}
            </p>
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="question-card">
            <h2 className="question-text">{currentQuestion.text}</h2>
            <div className="question-input-container">{renderQuestionInput(currentQuestion)}</div>
          </div>

          <div className="survey-navigation">
            {currentQuestionIndex > 0 && (
              <button
                type="button"
                className="nav-btn secondary"
                onClick={() => setCurrentQuestionIndex(currentQuestionIndex - 1)}
                disabled={submitting}
              >
                ← Назад
              </button>
            )}
            <button
              type="button"
              className="nav-btn primary"
              onClick={handleNext}
              disabled={submitting || !answers[currentQuestion.id]?.trim()}
            >
              {currentQuestionIndex < questions.length - 1 ? 'Далее →' : 'Завершить опрос'}
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}


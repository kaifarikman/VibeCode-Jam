import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchDashboard, fetchProfile } from '../modules/auth/api'
import type { DashboardSnapshot, UserProfile } from '../modules/auth/types'
import { fetchMyAnswers, fetchQuestions, submitAnswer } from '../modules/questions/api'
import type { Question } from '../modules/questions/types'
import '../App.css'
import './DashboardPage.css'

const TOKEN_STORAGE_KEY = 'vibecode_token'

export function DashboardPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState<UserProfile | null>(null)
  const [dashboard, setDashboard] = useState<DashboardSnapshot | null>(null)
  const [showSurvey, setShowSurvey] = useState(false)
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [surveyCompleted, setSurveyCompleted] = useState(false)
  const [surveyLoading, setSurveyLoading] = useState(false)

  useEffect(() => {
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) {
      navigate('/')
      return
    }
    void loadData(token)
  }, [navigate])

  const loadData = async (token: string) => {
    try {
      const [profile, snapshot] = await Promise.all([
        fetchProfile(token),
        fetchDashboard(token),
      ])
      setUser(profile)
      setDashboard(snapshot)
    } catch (error) {
      console.error('Failed to load profile:', error)
      handleLogout()
    }
    void loadQuestionsAndAnswers(token)
  }

  const loadQuestionsAndAnswers = async (token: string) => {
    try {
      const questionsData = await fetchQuestions(token)
      setQuestions(questionsData)

      const answersData = await fetchMyAnswers(token)
      const answersMap: Record<string, string> = {}
      answersData.forEach((answer) => {
        answersMap[answer.question_id] = answer.text
      })
      setAnswers(answersMap)

      if (questionsData.length > 0 && answersData.length === questionsData.length) {
        const allAnswered = questionsData.every((q) => answersMap[q.id]?.trim())
        if (allAnswered) {
          setSurveyCompleted(true)
        }
      }
    } catch (error) {
      console.error('Failed to load questions/answers:', error)
    }
  }

  const handleSubmitAnswer = async (questionId: string, text: string) => {
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) return
    try {
      setSurveyLoading(true)
      await submitAnswer(token, questionId, { question_id: questionId, text })
      setAnswers((prev) => ({ ...prev, [questionId]: text }))
    } catch (error) {
      console.error('Failed to submit answer:', error)
    } finally {
      setSurveyLoading(false)
    }
  }

  const handleLogout = () => {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY)
    navigate('/')
  }

  if (!user) {
    return <div>Загрузка...</div>
  }

  return (
    <div className="screen">
      <section className="dashboard-screen">
        <div>
          <p className="eyebrow">
            {user.is_verified ? 'Аккаунт подтверждён' : 'Email не подтвержден'}
          </p>
          <h1>Привет, {user.full_name ?? user.email}!</h1>
          <p className="subtitle">
            Мы сохранили твои настройки и готовы запустить редактор, когда захочешь.
          </p>
          {dashboard && (
            <ul className="stats">
              <li>
                <span>Последний статус</span>
                <strong>{dashboard.last_executor_status}</strong>
              </li>
              <li>
                <span>Очередь</span>
                <strong>{dashboard.pending_jobs}</strong>
              </li>
              <li>
                <span>Язык</span>
                <strong>{dashboard.last_language}</strong>
              </li>
            </ul>
          )}
        </div>

        {!surveyCompleted && questions.length > 0 && (
          <>
            {!showSurvey ? (
              <div className="survey-prompt">
                <div className="survey-icon">📋</div>
                <p>Помоги нам улучшить сервис — пройди опрос ({questions.length} вопросов)</p>
                <div className="survey-actions">
                  <button
                    type="button"
                    className="survey-btn primary"
                    onClick={() => {
                      setShowSurvey(true)
                      setCurrentQuestionIndex(0)
                    }}
                  >
                    Пройти опрос
                  </button>
                  <button
                    type="button"
                    className="survey-btn ghost"
                    onClick={() => setSurveyCompleted(true)}
                  >
                    Пропустить
                  </button>
                </div>
              </div>
            ) : (
              <div className="survey-section">
                <div className="survey-header">
                  <h3>
                    Вопрос {currentQuestionIndex + 1} из {questions.length}
                  </h3>
                  <button
                    type="button"
                    className="close-survey"
                    onClick={() => {
                      setShowSurvey(false)
                      if (Object.keys(answers).length === questions.length) {
                        setSurveyCompleted(true)
                      }
                    }}
                    aria-label="Закрыть опрос"
                  >
                    ×
                  </button>
                </div>
                <div className="survey-content">
                  {currentQuestionIndex < questions.length && (
                    <>
                      <p className="survey-question">
                        {questions[currentQuestionIndex].text}
                      </p>
                      <label className="survey-text-input">
                        <span className="label-text">Ваш ответ</span>
                        <textarea
                          value={answers[questions[currentQuestionIndex].id] || ''}
                          onChange={(e) =>
                            setAnswers({
                              ...answers,
                              [questions[currentQuestionIndex].id]: e.target.value,
                            })
                          }
                          placeholder="Введите ваш ответ..."
                          rows={4}
                          required
                        />
                      </label>
                      <div className="survey-navigation">
                        {currentQuestionIndex > 0 && (
                          <button
                            type="button"
                            className="survey-btn ghost"
                            onClick={() => setCurrentQuestionIndex(currentQuestionIndex - 1)}
                          >
                            ← Назад
                          </button>
                        )}
                        <button
                          type="button"
                          className="survey-submit"
                          disabled={
                            !answers[questions[currentQuestionIndex].id]?.trim() ||
                            surveyLoading
                          }
                          onClick={async () => {
                            const question = questions[currentQuestionIndex]
                            const answerText = answers[question.id]
                            if (answerText?.trim()) {
                              await handleSubmitAnswer(question.id, answerText)
                              if (currentQuestionIndex < questions.length - 1) {
                                setCurrentQuestionIndex(currentQuestionIndex + 1)
                              } else {
                                setShowSurvey(false)
                                setSurveyCompleted(true)
                              }
                            }
                          }}
                        >
                          {currentQuestionIndex < questions.length - 1
                            ? 'Далее →'
                            : 'Завершить'}
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        <div className="dashboard-actions">
          <button type="button" className="ghost" onClick={handleLogout}>
            Выйти
          </button>
          {user.is_admin && (
            <button
              type="button"
              className="admin-link-btn"
              onClick={() => navigate('/admin')}
            >
              🔧 Админка
            </button>
          )}
          <button type="button" className="primary" onClick={() => navigate('/ide')}>
            Перейти в редактор
          </button>
        </div>
      </section>
    </div>
  )
}


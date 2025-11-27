import { useEffect, useState } from 'react'
import {
  fetchApplicationsForModeration,
  fetchApplicationDetails,
  decideApplication,
  type ApplicationDetail,
} from '../modules/moderator/api'
import type { Application } from '../modules/vacancies/types'
import './ModeratorPanel.css'

interface ModeratorPanelProps {
  token: string
  onLogout: () => void
}

export function ModeratorPanel({ token, onLogout }: ModeratorPanelProps) {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedApplication, setSelectedApplication] = useState<ApplicationDetail | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [decisionComment, setDecisionComment] = useState('')
  const [processingDecision, setProcessingDecision] = useState(false)

  useEffect(() => {
    void loadApplications()
  }, [])

  const loadApplications = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchApplicationsForModeration(token)
      setApplications(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки заявок')
    } finally {
      setLoading(false)
    }
  }

  const handleViewApplication = async (applicationId: string) => {
    try {
      setError(null)
      const details = await fetchApplicationDetails(token, applicationId)
      setSelectedApplication(details)
      setShowDetails(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки деталей заявки')
    }
  }

  const handleDecide = async (decision: 'accepted' | 'rejected') => {
    if (!selectedApplication) return

    if (!confirm(`Вы уверены, что хотите ${decision === 'accepted' ? 'принять' : 'отклонить'} эту заявку?`)) {
      return
    }

    try {
      setProcessingDecision(true)
      setError(null)
      await decideApplication(token, selectedApplication.application.id, decision, decisionComment || undefined)
      alert(`Заявка ${decision === 'accepted' ? 'принята' : 'отклонена'}. Письмо отправлено кандидату.`)
      setShowDetails(false)
      setSelectedApplication(null)
      setDecisionComment('')
      await loadApplications()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка принятия решения')
    } finally {
      setProcessingDecision(false)
    }
  }

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: 'Принято',
      survey_completed: 'Опрос завершен',
      algo_test_completed: 'Алготест завершен',
      under_review: 'В рассмотрении',
      accepted: 'Принято',
      rejected: 'Отклонено',
    }
    return labels[status] || status
  }

  if (loading) {
    return (
      <div className="moderator-panel">
        <div className="loading-spinner">Загрузка заявок...</div>
      </div>
    )
  }

  if (showDetails && selectedApplication) {
    const app = selectedApplication.application
    return (
      <div className="moderator-panel">
        <header className="moderator-header">
          <h1>Панель модератора</h1>
          <div className="moderator-actions">
            <button type="button" className="btn-secondary" onClick={() => {
              setShowDetails(false)
              setSelectedApplication(null)
              setDecisionComment('')
            }}>
              ← Назад к списку
            </button>
            <button type="button" className="btn-logout" onClick={onLogout}>
              Выйти
            </button>
          </div>
        </header>

        <div className="moderator-content">
          <div className="application-details">
            <div className="detail-section candidate-header">
              <h2 className="candidate-title">{app.user_full_name || app.user_email} - {app.vacancy_title}</h2>
              <div className="detail-card">
                <div className="info-grid">
                  <div className="info-item">
                    <strong>Имя:</strong> {app.user_full_name || 'Не указано'}
                  </div>
                  <div className="info-item">
                    <strong>Email:</strong> {app.user_email}
                  </div>
                  <div className="info-item">
                    <strong>Вакансия:</strong> {app.vacancy_title}
                  </div>
                  <div className="info-item">
                    <strong>Позиция:</strong> {app.vacancy_position}
                  </div>
                  <div className="info-item">
                    <strong>Оценка ML:</strong> {app.ml_score ? app.ml_score.toFixed(2) : 'N/A'}
                  </div>
                  <div className="info-item">
                    <strong>Статус:</strong> <span className={`status-badge status-${app.status}`}>{getStatusLabel(app.status)}</span>
                  </div>
                  <div className="info-item">
                    <strong>Создана:</strong> {new Date(app.created_at).toLocaleString('ru-RU')}
                  </div>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h2>Решения алгоритмических задач ({selectedApplication.task_solutions.length})</h2>
              {selectedApplication.task_solutions.length === 0 ? (
                <div className="empty-state">Нет решений задач</div>
              ) : (
                selectedApplication.task_solutions.map((sol, idx) => (
                  <div key={sol.task_id} className="solution-card">
                    <h3>Задача {idx + 1}: {sol.task_title}</h3>
                    <p><strong>Статус:</strong> {sol.status === 'solved' ? '✓ Решена' : 'Попытка'}</p>
                    <p><strong>Вердикт:</strong> {sol.verdict || 'N/A'}</p>
                    <p><strong>Язык:</strong> {sol.language}</p>
                    {sol.metric && (
                      <div className="solution-metrics">
                        <div>
                          <strong>Тесты:</strong> {sol.metric.tests_passed ?? 0}/{sol.metric.tests_total ?? 0}
                        </div>
                        <div>
                          <strong>Среднее время:</strong> {sol.metric.average_duration_ms ? `${sol.metric.average_duration_ms} мс` : '—'}
                        </div>
                        <div>
                          <strong>Суммарное время:</strong> {sol.metric.total_duration_ms ? `${sol.metric.total_duration_ms} мс` : '—'}
                        </div>
                      </div>
                    )}
                    <details>
                      <summary>Условие задачи</summary>
                      <div className="task-description">{sol.task_description}</div>
                    </details>
                    <details>
                      <summary>Код решения</summary>
                      <pre className="code-block">{sol.solution_code || 'Нет кода'}</pre>
                    </details>
                  </div>
                ))
              )}
            </div>

            <div className="detail-section">
              <h2>Ответы на вопросы опроса ({selectedApplication.survey_answers.length})</h2>
              {selectedApplication.survey_answers.length === 0 ? (
                <div className="empty-state">Нет ответов на вопросы</div>
              ) : (
                selectedApplication.survey_answers.map((ans, idx) => (
                  <div key={ans.question_id} className="answer-card">
                    <h3>Вопрос {idx + 1}</h3>
                    <p><strong>Вопрос:</strong> {ans.question_text}</p>
                    <p><strong>Ответ:</strong> {ans.answer_text}</p>
                  </div>
                ))
              )}
            </div>

            <div className="detail-section decision-section">
              <h2>Решение по заявке</h2>
              <textarea
                className="comment-input"
                value={decisionComment}
                onChange={(e) => setDecisionComment(e.target.value)}
                placeholder="Комментарий (опционально)"
                rows={4}
              />
              <div className="decision-buttons">
                <button
                  type="button"
                  className="btn-accept"
                  onClick={() => handleDecide('accepted')}
                  disabled={processingDecision}
                >
                  ✓ Принять
                </button>
                <button
                  type="button"
                  className="btn-reject"
                  onClick={() => handleDecide('rejected')}
                  disabled={processingDecision}
                >
                  ✗ Отклонить
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="moderator-panel">
      <header className="moderator-header">
        <h1>Панель модератора</h1>
        <button type="button" className="btn-logout" onClick={onLogout}>
          Выйти
        </button>
      </header>

      <div className="moderator-content">
        {error && <div className="error-message">{error}</div>}

        <div className="applications-section">
          <h2>Заявки для модерации ({applications.length})</h2>
          {applications.length === 0 ? (
            <div className="empty-state">Нет заявок для модерации</div>
          ) : (
            <div className="applications-list">
              {applications.map((app) => {
                const userEmail = app.user?.email || 'Неизвестно'
                const userFullName = app.user?.full_name || null
                const candidateName = userFullName || userEmail
                const vacancyTitle = app.vacancy?.title || 'Неизвестная вакансия'
                
                return (
                  <div 
                    key={app.id} 
                    className="application-card"
                    onClick={() => handleViewApplication(app.id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <div className="application-header">
                      <h3 className="application-title">
                        {candidateName} - {vacancyTitle}
                      </h3>
                      <span className={`status-badge status-${app.status}`}>
                        {getStatusLabel(app.status)}
                      </span>
                    </div>
                    <div className="application-info">
                      <p><strong>Email:</strong> {userEmail}</p>
                      <p><strong>Оценка ML:</strong> {app.ml_score ? app.ml_score.toFixed(2) : 'N/A'}</p>
                      <p><strong>Создана:</strong> {new Date(app.created_at).toLocaleDateString('ru-RU')}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchVacancy, getMyApplications } from '../modules/vacancies/api'
import type { Application, Vacancy } from '../modules/vacancies/types'
import '../App.css'
import './VacancyDetailPage.css'

export function VacancyDetailPage() {
  const navigate = useNavigate()
  const { vacancyId } = useParams<{ vacancyId: string }>()
  const [vacancy, setVacancy] = useState<Vacancy | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [application, setApplication] = useState<Application | null>(null)

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
    void loadData(token, vacancyId)
  }, [vacancyId, navigate])

  const loadData = async (token: string, id: string) => {
    try {
      setLoading(true)
      setError(null)
      const [vacancyData, applications] = await Promise.all([
        fetchVacancy(token, id),
        getMyApplications(token),
      ])
      setVacancy(vacancyData)
      
      // Находим заявку для этой вакансии
      const app = applications.find(a => a.vacancy_id === id)
      setApplication(app || null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки данных')
    } finally {
      setLoading(false)
    }
  }

  const handleStartTest = async () => {
    const token = window.localStorage.getItem('vibecode_token')
    if (!token || !vacancyId) return

    try {
      // Если заявки нет, создаем её перед началом опроса
      if (!application) {
        const { applyToVacancy } = await import('../modules/vacancies/api')
        await applyToVacancy(token, vacancyId)
        // После создания заявки перезагружаем данные
        await loadData(token, vacancyId)
      }
      
      // Проверяем, не пройден ли уже опрос
      if (application && application.status !== 'pending') {
        setError('Вы уже прошли опрос по этой вакансии. Повторное прохождение невозможно.')
        return
      }
      
      // Блокируем доступ, если заявка в рассмотрении, принята или отклонена
      if (application && ['under_review', 'accepted', 'rejected'].includes(application.status)) {
        setError('Доступ к тестам закрыт. Заявка находится на рассмотрении или уже обработана.')
        return
      }
      
      // Переходим к опросу
      navigate(`/survey?vacancy_id=${vacancyId}`)
    } catch (err) {
      console.error('Error starting test:', err)
      setError(err instanceof Error ? err.message : 'Ошибка при начале теста')
    }
  }
  
  const isTestCompleted = application && application.status !== 'pending'
  const isBlocked = application && ['under_review', 'accepted', 'rejected'].includes(application.status)
  const isSurveyCompleted = application && application.status === 'survey_completed'

  if (loading) {
    return (
      <div className="vacancy-detail-page">
        <div className="loading-spinner">Загрузка...</div>
      </div>
    )
  }

  if (error || !vacancy) {
    return (
      <div className="vacancy-detail-page">
        <div className="error-message">
          <p>{error || 'Вакансия не найдена'}</p>
          <button type="button" className="back-btn" onClick={() => navigate('/home')}>
            Вернуться на главную
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="vacancy-detail-page">
      <header className="vacancy-detail-header">
        <div className="logo">FUTURECAREER</div>
        <button type="button" className="back-btn" onClick={() => navigate('/home')}>
          ← Назад
        </button>
      </header>

      <section className="vacancy-detail-content">
        <div className="vacancy-detail-container">
          <div className="vacancy-detail-card">
            <h1 className="vacancy-detail-title">{vacancy.title}</h1>
            <div className="vacancy-detail-meta">
              <span className="vacancy-detail-position">{vacancy.position}</span>
              <div className="vacancy-detail-tags">
                <span className="vacancy-tag vacancy-tag-language">{vacancy.language}</span>
                <span className="vacancy-tag vacancy-tag-grade">{vacancy.grade}</span>
              </div>
            </div>

            <div className="vacancy-detail-section">
              <h2 className="section-heading">Описание</h2>
              <div className="vacancy-description">
                <p>{vacancy.ideal_resume}</p>
              </div>
            </div>

            <div className="vacancy-detail-actions">
              {isBlocked ? (
                <div className="test-blocked-message">
                  <p>
                    {application?.status === 'under_review' && '⏳ Заявка находится на рассмотрении'}
                    {application?.status === 'accepted' && '✅ Ваша заявка принята! Мы свяжемся с вами.'}
                    {application?.status === 'rejected' && '❌ К сожалению, ваша заявка была отклонена'}
                  </p>
                  <p className="test-status-info">
                    Доступ к тестам закрыт. Вы можете только просмотреть информацию о вакансии.
                  </p>
                </div>
              ) : isSurveyCompleted ? (
                <div className="test-completed-message">
                  <p>✅ Опрос завершен</p>
                  <p className="test-status">
                    Статус: Опрос завершен
                  </p>
                  <button
                    type="button"
                    className="start-test-btn"
                    onClick={() => vacancyId && navigate(`/contest/${vacancyId}`)}
                  >
                    Решить алгоритмический контест
                  </button>
                </div>
              ) : isTestCompleted ? (
                <div className="test-completed-message">
                  <p>✅ Тест уже пройден</p>
                  <p className="test-status">
                    Статус: {application?.status === 'survey_completed' ? 'Опрос завершен' :
                             application?.status === 'algo_test_completed' ? 'Алготест завершен' :
                             application?.status === 'final_verdict' ? 'Получен вердикт' : 'Завершено'}
                  </p>
                  {application?.status === 'survey_completed' && (
                    <button
                      type="button"
                      className="start-test-btn"
                      onClick={() => vacancyId && navigate(`/contest/${vacancyId}`)}
                    >
                      Решить алгоритмический контест
                    </button>
                  )}
                </div>
              ) : (
                <button
                  type="button"
                  className="start-test-btn"
                  onClick={handleStartTest}
                >
                  Пройти тест
                </button>
              )}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}


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

  const handleStartTest = () => {
    // Проверяем, не пройден ли уже тест
    if (application && application.status !== 'pending') {
      setError('Вы уже прошли тест по этой вакансии. Повторное прохождение невозможно.')
      return
    }
    
    if (vacancyId) {
      navigate(`/survey?vacancy_id=${vacancyId}`)
    }
  }
  
  const isTestCompleted = application && application.status !== 'pending'

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
              {isTestCompleted ? (
                <div className="test-completed-message">
                  <p>✅ Тест уже пройден</p>
                  <p className="test-status">
                    Статус: {application?.status === 'survey_completed' ? 'Прошел тест' :
                             application?.status === 'algo_test_completed' ? 'Прошел алготест' :
                             application?.status === 'final_verdict' ? 'Получен вердикт' : 'Завершено'}
                  </p>
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


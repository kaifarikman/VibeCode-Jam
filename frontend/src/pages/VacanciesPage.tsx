import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { fetchVacancies, applyToVacancy } from '../modules/vacancies/api'
import type { Vacancy } from '../modules/vacancies/types'
import '../App.css'
import './VacanciesPage.css'

export function VacanciesPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const language = searchParams.get('language') || ''
  const grade = searchParams.get('grade') || ''
  
  const [vacancies, setVacancies] = useState<Vacancy[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const token = window.localStorage.getItem('vibecode_token')
    if (!token) {
      navigate('/')
      return
    }
    if (!language || !grade) {
      navigate('/home')
      return
    }
    void loadVacancies(token)
  }, [language, grade, navigate])

  const loadVacancies = async (token: string) => {
    try {
      setLoading(true)
      const data = await fetchVacancies(token, language, grade)
      setVacancies(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки вакансий')
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async (vacancyId: string) => {
    const token = window.localStorage.getItem('vibecode_token')
    if (!token) return

    try {
      setError(null)
      
      const { application } = await applyToVacancy(token, vacancyId)
      
      if (application) {
        // Сразу перенаправляем на главную страницу после выбора вакансии
        navigate('/home')
      }
    } catch (err) {
      // Обрабатываем только реальные ошибки
      const errorMessage = err instanceof Error ? err.message : 'Ошибка подачи заявки'
      setError(errorMessage)
      console.error('Error applying to vacancy:', err)
    }
  }

  if (loading) {
    return (
      <div className="vacancies-page">
        <div className="loading">Загрузка вакансий...</div>
      </div>
    )
  }

  return (
    <div className="vacancies-page">
      <header className="vacancies-header">
        <div className="logo">FUTURECAREER</div>
        <div className="header-actions">
          <button type="button" className="back-btn" onClick={() => navigate('/home')}>
            ← Назад
          </button>
          <button
            type="button"
            className="logout-btn"
            onClick={() => {
              window.localStorage.removeItem('vibecode_token')
              navigate('/')
            }}
          >
            Выйти
          </button>
        </div>
      </header>

      <section className="vacancies-content">
        <div className="vacancies-container">
          <h1 className="vacancies-title">Доступные вакансии</h1>
          <p className="vacancies-subtitle">
            Язык: <strong>{language}</strong> | Грейд: <strong>{grade}</strong>
          </p>

          {error && <div className="error-message">{error}</div>}

          {vacancies.length === 0 ? (
            <div className="no-vacancies">
              <p>Вакансии не найдены</p>
              <button type="button" className="back-btn" onClick={() => navigate('/home')}>
                Вернуться к выбору
              </button>
            </div>
          ) : (
            <div className="vacancies-grid">
              {vacancies.map((vacancy) => (
                <div key={vacancy.id} className="vacancy-card">
                  <div className="vacancy-header">
                    <h2>{vacancy.title}</h2>
                    <span className="vacancy-position">{vacancy.position}</span>
                  </div>
                  <div className="vacancy-meta">
                    <span className="meta-item">Язык: {vacancy.language}</span>
                    <span className="meta-item">Грейд: {vacancy.grade}</span>
                  </div>
                  <div className="vacancy-description">
                    <h3>Идеальное резюме:</h3>
                    <p>{vacancy.ideal_resume}</p>
                  </div>
                  <button
                    type="button"
                    className="apply-btn"
                    onClick={() => handleApply(vacancy.id)}
                  >
                    Подать заявку
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}


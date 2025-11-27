import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchProfile } from '../modules/auth/api'
import type { UserProfile } from '../modules/auth/types'
import { getMyApplications } from '../modules/vacancies/api'
import type { Application } from '../modules/vacancies/types'
import '../App.css'
import './HomePage.css'

export function HomePage() {
  const navigate = useNavigate()
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [applications, setApplications] = useState<Application[]>([])
  const [loadingApplications, setLoadingApplications] = useState(true)

  useEffect(() => {
    const token = window.localStorage.getItem('vibecode_token')
    if (!token) {
      navigate('/')
      return
    }
    
    const loadProfile = async () => {
      try {
        const profile = await fetchProfile(token)
        setUser(profile)
      } catch (error) {
        console.error('Failed to load profile:', error)
        window.localStorage.removeItem('vibecode_token')
        navigate('/')
      } finally {
        setLoading(false)
      }
    }
    
    const loadApplications = async () => {
      try {
        setLoadingApplications(true)
        const apps = await getMyApplications(token)
        setApplications(apps)
      } catch (error) {
        console.error('Failed to load applications:', error)
      } finally {
        setLoadingApplications(false)
      }
    }
    
    void loadProfile()
    void loadApplications()
    
    // Обновляем список при фокусе на странице (когда пользователь возвращается)
    const handleFocus = () => {
      if (token) {
        void loadApplications()
      }
    }
    
    window.addEventListener('focus', handleFocus)
    return () => {
      window.removeEventListener('focus', handleFocus)
    }
  }, [navigate])


  if (loading) {
    return (
      <div className="home-page">
        <div className="loading-spinner">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="home-page">
      <header className="home-header">
        <div className="logo">FUTURECAREER</div>
        <div className="user-info">
          {user?.full_name && (
            <span className="user-name">{user.full_name}</span>
          )}
          <button type="button" className="logout-btn" onClick={() => {
            window.localStorage.removeItem('vibecode_token')
            navigate('/')
          }}>
            Выйти
          </button>
        </div>
      </header>

      <section className="home-content">
        <div className="home-container">
          <h1 className="home-title">Добро пожаловать!</h1>
          <p className="home-subtitle">Управляйте своими вакансиями и проходите тесты</p>

          {/* Список выбранных вакансий */}
          {applications.length > 0 && (
            <div className="applications-section">
              <h2 className="section-title">Мои вакансии</h2>
              <div className="applications-list">
                {applications.map((app) => (
                  <div
                    key={app.id}
                    className="application-card"
                  >
                    {app.vacancy && (
                      <>
                        <div onClick={() => navigate(`/vacancy/${app.vacancy_id}`)}>
                          <h3 className="vacancy-title">{app.vacancy.title}</h3>
                          <p className="vacancy-position">{app.vacancy.position}</p>
                          <div className="vacancy-meta">
                            <span className="vacancy-language">{app.vacancy.language}</span>
                            <span className="vacancy-grade">{app.vacancy.grade}</span>
                            <span className={`application-status status-${app.status}`}>
                              {app.status === 'pending' ? 'Принято' : 
                               app.status === 'survey_completed' ? 'Опрос завершен' :
                               app.status === 'algo_test_completed' ? 'Алготест завершен' :
                               app.status === 'final_verdict' ? 'Получен вердикт' : 'Неизвестно'}
                            </span>
                          </div>
                        </div>
                        {app.status === 'survey_completed' && (
                          <button
                            type="button"
                            className="contest-btn"
                            onClick={(e) => {
                              e.stopPropagation()
                              navigate(`/contest/${app.vacancy_id}`)
                            }}
                          >
                            Решить алгоритмический контест
                          </button>
                        )}
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Кнопка для выбора вакансий */}
          <div className="select-vacancy-section">
            <button
              type="button"
              className="select-vacancy-btn"
              onClick={() => navigate('/select-vacancy')}
            >
              Выбрать вакансии
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}


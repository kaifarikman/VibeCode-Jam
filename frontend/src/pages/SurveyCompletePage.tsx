import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import '../App.css'
import './SurveyCompletePage.css'

export function SurveyCompletePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const vacancyId = searchParams.get('vacancy_id') || ''
  const mlScore = searchParams.get('ml_score') || '0'

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
  }, [vacancyId, navigate])

  const handleGoHome = () => {
    navigate('/home')
  }

  return (
    <div className="survey-complete-page">
      <header className="survey-complete-header">
        <div className="logo">FUTURECAREER</div>
      </header>

      <section className="survey-complete-content">
        <div className="survey-complete-container">
          <div className="success-icon">🎉</div>
          <h1 className="congratulations-title">Поздравляем!</h1>
          <p className="congratulations-text">
            Вы успешно прошли опрос по вакансии
          </p>
          
          <div className="next-steps">
            <p>Следующий этап - решение алгоритмических задач</p>
          </div>

          <button
            type="button"
            className="home-button"
            onClick={handleGoHome}
          >
            Вернуться на главную
          </button>
        </div>
      </section>
    </div>
  )
}


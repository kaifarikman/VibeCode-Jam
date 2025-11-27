import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import '../App.css'

const TOKEN_STORAGE_KEY = 'vibecode_token'

export function ContestCompletePage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const vacancyId = searchParams.get('vacancy_id')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) {
      navigate('/')
      return
    }
    setLoading(false)
  }, [navigate])

  const handleGoHome = () => {
    navigate('/home')
  }

  if (loading) {
    return (
      <div className="app-container">
        <div className="loading-state">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="app-container">
      <div className="contest-complete-container">
        <div className="contest-complete-card">
          <div className="success-icon">✓</div>
          <h1 className="contest-complete-title">Поздравляем!</h1>
          <p className="contest-complete-message">
            Вы успешно прошли все этапы собеседования:
          </p>
          <ul className="contest-complete-steps">
            <li>✓ Опрос для резюме</li>
            <li>✓ Алгоритмический контест</li>
          </ul>
          <p className="contest-complete-info">
            Ваша заявка отправлена на рассмотрение модераторам.
            Мы свяжемся с вами в ближайшее время по результатам рассмотрения.
          </p>
          <button
            type="button"
            className="contest-complete-button"
            onClick={handleGoHome}
          >
            Вернуться в главное меню
          </button>
        </div>
      </div>
    </div>
  )
}


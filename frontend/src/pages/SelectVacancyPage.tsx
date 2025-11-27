import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchProfile } from '../modules/auth/api'
import type { UserProfile } from '../modules/auth/types'
import '../App.css'
import './SelectVacancyPage.css'

type SupportedLanguage = 'python' | 'typescript' | 'go' | 'java'
type Grade = 'junior' | 'middle' | 'senior'

const LANGUAGES: { value: SupportedLanguage; label: string }[] = [
  { value: 'python', label: 'Python' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'go', label: 'Go' },
  { value: 'java', label: 'Java' },
]

const GRADES: { value: Grade; label: string }[] = [
  { value: 'junior', label: 'Junior' },
  { value: 'middle', label: 'Middle' },
  { value: 'senior', label: 'Senior' },
]

export function SelectVacancyPage() {
  const navigate = useNavigate()
  const [selectedLanguage, setSelectedLanguage] = useState<SupportedLanguage | null>(null)
  const [selectedGrade, setSelectedGrade] = useState<Grade | null>(null)
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

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
    
    void loadProfile()
  }, [navigate])

  const handleContinue = () => {
    if (selectedLanguage && selectedGrade) {
      // Сохраняем выбор в localStorage
      window.localStorage.setItem('selected_language', selectedLanguage)
      window.localStorage.setItem('selected_grade', selectedGrade)
      // Переход на страницу выбора вакансий
      navigate(`/vacancies?language=${selectedLanguage}&grade=${selectedGrade}`)
    }
  }

  if (loading) {
    return (
      <div className="select-vacancy-page">
        <div className="loading-spinner">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="select-vacancy-page">
      <header className="select-vacancy-header">
        <div className="logo">FUTURECAREER</div>
        <div className="user-info">
          {user?.full_name && (
            <span className="user-name">{user.full_name}</span>
          )}
          <button type="button" className="back-btn" onClick={() => navigate('/home')}>
            ← Назад
          </button>
        </div>
      </header>

      <section className="select-vacancy-content">
        <div className="select-vacancy-container">
          <h1 className="select-vacancy-title">Выберите параметры</h1>
          <p className="select-vacancy-subtitle">Укажите язык программирования и ваш уровень</p>

          <div className="selection-cards">
            <div className="selection-card">
              <h2>Язык программирования</h2>
              <div className="options-grid">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.value}
                    type="button"
                    className={`option-btn ${selectedLanguage === lang.value ? 'active' : ''}`}
                    onClick={() => setSelectedLanguage(lang.value)}
                  >
                    {lang.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="selection-card">
              <h2>Грейд</h2>
              <div className="options-grid">
                {GRADES.map((grade) => (
                  <button
                    key={grade.value}
                    type="button"
                    className={`option-btn ${selectedGrade === grade.value ? 'active' : ''}`}
                    onClick={() => setSelectedGrade(grade.value)}
                  >
                    {grade.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button
            type="button"
            className="continue-btn"
            onClick={handleContinue}
            disabled={!selectedLanguage || !selectedGrade}
          >
            Продолжить
          </button>
        </div>
      </section>
    </div>
  )
}


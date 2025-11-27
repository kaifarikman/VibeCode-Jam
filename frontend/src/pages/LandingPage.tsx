import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { AuthForm, type AuthFormMode } from '../components/AuthForm'
import { login, registerUser, verifyRegistration, requestLoginCode } from '../modules/auth/api'
import type { AuthStage } from '../modules/auth/types'
import '../App.css'
import './LandingPage.css'

export function LandingPage() {
  const navigate = useNavigate()
  const [authStage, setAuthStage] = useState<AuthStage>('landing')
  const [authFormMode, setAuthFormMode] = useState<AuthFormMode>('login')
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)
  const [authInfo, setAuthInfo] = useState<string | null>(null)
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [pendingEmail, setPendingEmail] = useState<string | null>(null)
  const [code, setCode] = useState('')

  const resetAuthStatus = () => {
    setAuthError(null)
    setAuthInfo(null)
  }

  const closeAuthModal = () => {
    setAuthStage('landing')
    resetAuthStatus()
    setAuthLoading(false)
    setPassword('')
    setCode('')
    setPendingEmail(null)
  }

  const startAuthFlow = (stage: Exclude<AuthStage, 'landing'>) => {
    setAuthStage(stage)
    setAuthFormMode(stage === 'verify' ? 'verify' : stage)
    resetAuthStatus()
    if (stage === 'register') {
      setPendingEmail(null)
      setPassword('')
    }
  }

  const handleLoginSubmit = async (event: FormEvent) => {
    event.preventDefault()
    
    // Валидация на фронтенде перед отправкой
    if (!email || !email.includes('@')) {
      setAuthError('Введите корректный email адрес')
      return
    }
    
    if (!password || password.length < 8) {
      setAuthError('Пароль должен содержать минимум 8 символов')
      return
    }
    
    setAuthLoading(true)
    resetAuthStatus()
    try {
      const data = await login({ email, password })
      window.localStorage.setItem('vibecode_token', data.access_token)
      setPassword('')
      closeAuthModal()
      setAuthLoading(false)
      // Прямое перенаправление через window.location для гарантированного перехода
      window.location.href = '/home'
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Не удалось войти'
      // Улучшаем сообщения об ошибках
      let displayMessage = errorMessage
      if (errorMessage.includes('value is not a valid email')) {
        displayMessage = 'Введите корректный email адрес'
      } else if (errorMessage.includes('ensure this value has at least') || errorMessage.includes('минимум')) {
        displayMessage = 'Пароль должен содержать минимум 8 символов'
      } else if (errorMessage.includes('Неверный email') || errorMessage.includes('пароль')) {
        displayMessage = 'Неверный email или пароль'
      }
      setAuthError(displayMessage)
      setAuthLoading(false)
    }
  }

  const handleRegisterSubmit = async (event: FormEvent) => {
    event.preventDefault()
    
    // Валидация на фронтенде перед отправкой
    if (!email || !email.includes('@')) {
      setAuthError('Введите корректный email адрес')
      return
    }
    
    if (!password || password.length < 8) {
      setAuthError('Пароль должен содержать минимум 8 символов')
      return
    }
    
    if (!fullName || fullName.trim().split(/\s+/).length < 3) {
      setAuthError('ФИО должно содержать минимум 3 слова (Фамилия Имя Отчество)')
      return
    }
    
    setAuthLoading(true)
    resetAuthStatus()
    try {
      await registerUser({ email, fullName, password })
      setPendingEmail(email)
      setAuthStage('verify')
      setAuthFormMode('verify')
      setAuthInfo(`Мы отправили код подтверждения на ${email}.`)
      setCode('')
      setAuthError(null)
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Не удалось отправить код'
      // Улучшаем сообщения об ошибках
      let displayMessage = errorMessage
      if (errorMessage.includes('value is not a valid email')) {
        displayMessage = 'Введите корректный email адрес'
      } else if (errorMessage.includes('ensure this value has at least') || errorMessage.includes('минимум')) {
        displayMessage = 'Пароль должен содержать минимум 8 символов'
      } else if (errorMessage.includes('ФИО') || errorMessage.includes('3 слова')) {
        displayMessage = 'ФИО должно содержать минимум 3 слова (Фамилия Имя Отчество)'
      } else if (errorMessage.includes('уже зарегистрирован')) {
        displayMessage = 'Пользователь с таким email уже зарегистрирован. Выполните вход.'
      }
      setAuthError(displayMessage)
    } finally {
      setAuthLoading(false)
    }
  }

  const handleVerifySubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!(pendingEmail || email)) {
      setAuthError('Укажите e-mail, который использовали при регистрации')
      return
    }
    
    // Валидация кода
    if (!code || code.length !== 6 || !/^\d+$/.test(code)) {
      setAuthError('Введите 6-значный код подтверждения')
      return
    }
    
    setAuthLoading(true)
    resetAuthStatus()
    try {
      const data = await verifyRegistration({
        email: pendingEmail ?? email,
        code,
      })
      window.localStorage.setItem('vibecode_token', data.access_token)
      setCode('')
      closeAuthModal()
      setAuthLoading(false)
      // Прямое перенаправление через window.location для гарантированного перехода
      window.location.href = '/home'
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Не удалось подтвердить код'
      // Улучшаем сообщения об ошибках
      let displayMessage = errorMessage
      if (errorMessage.includes('Неверный код') || errorMessage.includes('истёк')) {
        displayMessage = 'Неверный код подтверждения или код истёк. Запросите новый код.'
      } else if (errorMessage.includes('value is not a valid email')) {
        displayMessage = 'Введите корректный email адрес'
      } else if (errorMessage.includes('ensure this value has at least')) {
        displayMessage = 'Код должен содержать 6 цифр'
      }
      setAuthError(displayMessage)
      setAuthLoading(false)
    }
  }

  const handleRequestCode = async () => {
    setAuthLoading(true)
    resetAuthStatus()
    try {
      const targetEmail = pendingEmail || email
      if (!targetEmail) {
        throw new Error('Email для запроса кода не найден.')
      }
      await requestLoginCode({ email: targetEmail })
      setAuthInfo('Новый код отправлен на вашу почту.')
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Ошибка отправки кода')
    } finally {
      setAuthLoading(false)
    }
  }

  return (
    <div className="landing-page">
      {/* Header with Logo */}
      <header className="landing-header">
        <div className="logo">FUTURECAREER</div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1>Пройди собеседование будущего прямо сейчас</h1>
          <p className="hero-subtitle">
            Объективная оценка ваших навыков с помощью машинных технологий
          </p>
          <div className="hero-actions">
            <button type="button" className="primary" onClick={() => startAuthFlow('login')}>
              Авторизоваться
            </button>
            <button
              type="button"
              className="ghost"
              onClick={() => startAuthFlow('register')}
            >
              Зарегистрироваться
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <h2 className="section-title">Почему выбирают нас</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Быстрая обратная связь</h3>
              <p>
                Получайте мгновенные результаты выполнения вашего кода
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Точная оценка</h3>
              <p>
                Наша система анализирует не только результат, но и качество кода, его эффективность и соответствие эталонным решениям
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌐</div>
              <h3>Доступность</h3>
              <p>
                Возможность пройти собеседование из любой точки мира, в любое время. Все что нужно - это интернет и желание развиваться
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3>Выбор направления</h3>
              <p>
                Выберите язык программирования и свой Грейд
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">💻</div>
              <h3>Написание решения</h3>
              <p>
                Используйте встроенный редактор кода для написания решения
              </p>
            </div>
          </div>
        </div>
      </section>


      {/* Contact Section */}
      <section className="contact-section">
        <div className="container">
          <h2 className="section-title">Свяжитесь с нами</h2>
          <div className="contact-info">
            <div className="contact-item">
              <div className="contact-icon">📧</div>
              <div>
                <h3>Email</h3>
                <a href="mailto:support@futurecareer.com">support@futurecareer.com</a>
              </div>
            </div>
            <div className="contact-item">
              <div className="contact-icon">📞</div>
              <div>
                <h3>Телефон</h3>
                <a href="tel:+78001234567">+7 (800) 123-45-67</a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Auth Modal */}
      {authStage !== 'landing' && (
        <div className="auth-modal-overlay" onClick={closeAuthModal}>
          <div
            className="auth-modal"
            onClick={(event) => {
              event.stopPropagation()
            }}
          >
            <button type="button" className="close-modal" onClick={closeAuthModal}>
              ×
            </button>
            <AuthForm
              mode={authFormMode}
              email={email}
              setEmail={setEmail}
              password={password}
              setPassword={setPassword}
              fullName={fullName}
              setFullName={setFullName}
              code={code}
              setCode={setCode}
              loading={authLoading}
              error={authError}
              info={authInfo}
              onSubmit={
                authFormMode === 'login'
                  ? handleLoginSubmit
                  : authFormMode === 'register'
                    ? handleRegisterSubmit
                    : handleVerifySubmit
              }
              onSwitchMode={(mode) => {
                setAuthFormMode(mode)
                if (mode === 'login') startAuthFlow('login')
                if (mode === 'register') startAuthFlow('register')
              }}
              onRequestCode={handleRequestCode}
              pendingEmail={pendingEmail}
            />
          </div>
        </div>
      )}
    </div>
  )
}

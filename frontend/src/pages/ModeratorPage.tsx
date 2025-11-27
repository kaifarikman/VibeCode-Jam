import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { FormEvent } from 'react'
import { ModeratorPanel } from '../components/ModeratorPanel'
import { AuthForm } from '../components/AuthForm'
import { moderatorLogin } from '../modules/auth/api'
import type { UserProfile } from '../modules/auth/types'
import '../App.css'
import './ModeratorPage.css'

const MODERATOR_TOKEN_STORAGE_KEY = 'vibecode_moderator_token'

export function ModeratorPage() {
  const navigate = useNavigate()
  const [token, setToken] = useState<string | null>(
    () => window.localStorage.getItem(MODERATOR_TOKEN_STORAGE_KEY)
  )
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  
  // Форма входа
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

  useEffect(() => {
    if (token) {
      void checkModeratorAccess()
    } else {
      setLoading(false)
    }
  }, [token])

  const checkModeratorAccess = async () => {
    try {
      // Не проверяем через fetchProfile, так как токен модератора не работает с /api/users/me
      // Просто считаем, что если токен есть, то модератор авторизован
      // Валидность токена проверится при загрузке заявок в ModeratorPanel
      setUser({
        id: '',
        email: 'moderator@example.com',
        full_name: null,
        is_admin: false,
        is_verified: true,
        created_at: new Date().toISOString(),
        last_login_at: null,
      } as UserProfile)
    } catch (error) {
      console.error('Failed to check moderator access:', error)
      setToken(null)
      window.localStorage.removeItem(MODERATOR_TOKEN_STORAGE_KEY)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const handleModeratorLogin = async (event: FormEvent) => {
    event.preventDefault()
    setAuthLoading(true)
    setAuthError(null)
    
    try {
      const data = await moderatorLogin({ email, password })
      const newToken = data.access_token
      // Сохраняем токен в отдельном ключе для модератора
      window.localStorage.setItem(MODERATOR_TOKEN_STORAGE_KEY, newToken)
      setToken(newToken)
      setPassword('')
      
      // Используем данные из ответа вместо fetchProfile
      // (токен модератора не работает с /api/users/me)
      setUser(data.user)
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Неверный email или пароль')
    } finally {
      setAuthLoading(false)
    }
  }

  const handleLogout = () => {
    setToken(null)
    window.localStorage.removeItem(MODERATOR_TOKEN_STORAGE_KEY)
    setUser(null)
  }

  if (loading) {
    return (
      <div className="moderator-page-loading">
        <div className="loading-spinner">Загрузка...</div>
      </div>
    )
  }

  // Если пользователь авторизован - показываем панель
  if (token && user) {
    return <ModeratorPanel token={token} onLogout={handleLogout} />
  }

  // Иначе показываем форму входа
  return (
    <div className="moderator-login-page">
      <div className="moderator-login-container">
        <div className="moderator-login-header">
          <h1>Вход в панель модератора</h1>
          <p>Введите учетные данные модератора</p>
        </div>
        
        <AuthForm
          mode="login"
          email={email}
          setEmail={setEmail}
          password={password}
          setPassword={setPassword}
          fullName=""
          setFullName={() => {}}
          code=""
          setCode={() => {}}
          loading={authLoading}
          error={authError}
          info={null}
          onSubmit={handleModeratorLogin}
          onSwitchMode={() => {}}
          hideRegister={true}
        />
        
        <div className="moderator-login-footer">
          <button
            type="button"
            className="btn-link"
            onClick={() => navigate('/')}
          >
            ← Вернуться на главную
          </button>
        </div>
      </div>
    </div>
  )
}


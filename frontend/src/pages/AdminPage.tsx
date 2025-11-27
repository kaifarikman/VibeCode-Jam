import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type { FormEvent } from 'react'
import { AdminPanel } from '../components/AdminPanel'
import { AuthForm } from '../components/AuthForm'
import { login, fetchProfile } from '../modules/auth/api'
import type { UserProfile } from '../modules/auth/types'
import '../App.css'
import './AdminPage.css'

const ADMIN_TOKEN_STORAGE_KEY = 'vibecode_admin_token'

export function AdminPage() {
  const navigate = useNavigate()
  const [token, setToken] = useState<string | null>(
    () => window.localStorage.getItem(ADMIN_TOKEN_STORAGE_KEY)
  )
  const [user, setUser] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [isAdmin, setIsAdmin] = useState(false)
  
  // Форма входа
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

  useEffect(() => {
    if (token) {
      void checkAdminAccess()
    } else {
      setLoading(false)
    }
  }, [token])

  const checkAdminAccess = async () => {
    try {
      const profile = await fetchProfile(token!)
      setUser(profile)
      setIsAdmin(profile.is_admin)
      // Если пользователь не админ, просто очищаем токен без показа ошибки
      // (ошибка будет показана только после попытки входа)
      if (!profile.is_admin) {
        setToken(null)
        window.localStorage.removeItem(ADMIN_TOKEN_STORAGE_KEY)
        setUser(null)
        setIsAdmin(false)
      }
    } catch (error) {
      console.error('Failed to check admin access:', error)
      setToken(null)
      window.localStorage.removeItem(ADMIN_TOKEN_STORAGE_KEY)
      setUser(null)
      setIsAdmin(false)
    } finally {
      setLoading(false)
    }
  }

  const handleAdminLogin = async (event: FormEvent) => {
    event.preventDefault()
    setAuthLoading(true)
    setAuthError(null)
    
    try {
      const data = await login({ email, password })
      const newToken = data.access_token
      // Сохраняем токен в отдельном ключе для админки
      window.localStorage.setItem(ADMIN_TOKEN_STORAGE_KEY, newToken)
      setToken(newToken)
      setPassword('')
      
      // Проверяем, является ли пользователь админом
      const profile = await fetchProfile(newToken)
      if (!profile.is_admin) {
        setAuthError('У вас нет прав доступа к админ-панели')
        window.localStorage.removeItem(ADMIN_TOKEN_STORAGE_KEY)
        setToken(null)
      } else {
        setUser(profile)
        setIsAdmin(true)
      }
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Неверный email или пароль')
    } finally {
      setAuthLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="admin-page-loading">
        <div className="loading-spinner">Загрузка...</div>
      </div>
    )
  }

  // Если пользователь авторизован и является админом - показываем панель
  if (token && isAdmin && user) {
    return <AdminPanel token={token} />
  }

  // Иначе показываем форму входа
  return (
    <div className="admin-login-page">
      <div className="admin-login-container">
        <div className="admin-login-header">
          <h1>Вход в админ-панель</h1>
          <p>Введите учетные данные администратора</p>
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
          onSubmit={handleAdminLogin}
          onSwitchMode={() => {}} // Отключаем переключение режимов
          hideRegister={true} // Скрываем кнопку регистрации
        />
        
        <div className="admin-login-footer">
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

import { type FormEvent, useState } from 'react'
import './AuthForm.css'

export type AuthFormMode = 'login' | 'register' | 'verify'

interface AuthFormProps {
  mode: AuthFormMode
  email: string
  setEmail: (email: string) => void
  password: string
  setPassword: (password: string) => void
  fullName: string
  setFullName: (fullName: string) => void
  code: string
  setCode: (code: string) => void
  loading: boolean
  error: string | null
  info: string | null
  onSubmit: (e: FormEvent) => void
  onSwitchMode: (mode: AuthFormMode) => void
  onRequestCode?: () => void
  pendingEmail?: string | null
  hideRegister?: boolean // Скрыть кнопку регистрации
}

export function AuthForm({
  mode,
  email,
  setEmail,
  password,
  setPassword,
  fullName,
  setFullName,
  code,
  setCode,
  loading,
  error,
  info,
  onSubmit,
  onSwitchMode,
  onRequestCode,
  pendingEmail,
  hideRegister = false,
}: AuthFormProps) {
  return (
    <div className="auth-form-container">
      <div className="auth-form-header">
        <h1>
          {mode === 'login' && 'Вход'}
          {mode === 'register' && 'Регистрация'}
          {mode === 'verify' && 'Подтверждение email'}
        </h1>
        <p className="auth-form-subtitle">
          {mode === 'login' && 'Войдите в свой аккаунт'}
          {mode === 'register' && 'Создайте новый аккаунт'}
          {mode === 'verify' && 'Введите код подтверждения'}
        </p>
      </div>

      <form className="auth-form" onSubmit={onSubmit}>
        {mode === 'login' && (
          <>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Пароль</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Вход...' : 'Войти'}
            </button>
            {!hideRegister && (
              <button
                type="button"
                className="btn-link"
                onClick={() => onSwitchMode('register')}
                disabled={loading}
              >
                Нет аккаунта? Зарегистрироваться
              </button>
            )}
          </>
        )}

        {mode === 'register' && (
          <>
            <div className="form-group">
              <label htmlFor="reg-email">Email</label>
              <input
                id="reg-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="reg-password">Пароль</label>
              <input
                id="reg-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Минимум 8 символов"
                minLength={8}
                required
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="full-name">ФИО</label>
              <input
                id="full-name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Иванов Иван Иванович"
                disabled={loading}
                required
                pattern="\S+\s+\S+\s+\S+.*"
                title="Введите минимум 3 слова (Фамилия Имя Отчество)"
              />
              <small className="form-hint">Обязательное поле. Минимум 3 слова</small>
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
            <button
              type="button"
              className="btn-link"
              onClick={() => onSwitchMode('login')}
              disabled={loading}
            >
              Уже есть аккаунт? Войти
            </button>
          </>
        )}

        {mode === 'verify' && (
          <>
            <div className="verify-info">
              <p>
                Введите 6-значный код, который пришёл на{' '}
                <strong>{pendingEmail || email}</strong>
              </p>
            </div>
            <div className="form-group">
              <label htmlFor="code">Код подтверждения</label>
              <input
                id="code"
                type="text"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="000000"
                minLength={6}
                maxLength={6}
                required
                disabled={loading}
                className="code-input"
              />
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Проверка...' : 'Подтвердить'}
            </button>
            {onRequestCode && (
              <button
                type="button"
                className="btn-link"
                onClick={onRequestCode}
                disabled={loading}
              >
                Запросить код ещё раз
              </button>
            )}
          </>
        )}

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">⚠</span>
            <span className="alert-message">{error}</span>
          </div>
        )}

        {info && (
          <div className="alert alert-info">
            <span className="alert-icon">ℹ</span>
            <span className="alert-message">{info}</span>
          </div>
        )}
      </form>
    </div>
  )
}


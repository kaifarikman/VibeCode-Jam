import { type FormEvent, useEffect, useMemo, useState } from 'react'
import Editor from '@monaco-editor/react'
import './App.css'
import { fetchDashboard, fetchProfile, login, registerUser, verifyRegistration } from './modules/auth/api'
import type {
  AuthStage,
  DashboardSnapshot,
  UserProfile,
} from './modules/auth/types'
import {
  defaultConsole,
  quickTests,
  runtimeTargets,
  sampleFiles,
  type ConsoleLine,
  type IdeFile,
} from './modules/ide/sampleWorkspace'
import { fetchMyAnswers, fetchQuestions, submitAnswer } from './modules/questions/api'
import type { Question } from './modules/questions/types'
import { AdminPanel } from './components/AdminPanel'

const TOKEN_STORAGE_KEY = 'vibecode_token'
type ViewMode = 'landing' | 'dashboard' | 'ide' | 'admin'

const timestamp = () =>
  new Intl.DateTimeFormat('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(new Date())

type ConsoleLevel = ConsoleLine['level']

const createLog = (message: string, level: ConsoleLevel = 'info'): ConsoleLine => ({
  id: `${level}-${crypto.randomUUID()}`,
  level,
  message,
  timestamp: timestamp(),
})

function App() {
  const [files, setFiles] = useState<IdeFile[]>(sampleFiles)
  const [activeFileId, setActiveFileId] = useState(sampleFiles[0]?.id ?? '')
  const [consoleLines, setConsoleLines] = useState<ConsoleLine[]>(defaultConsole)
  const [selectedRuntime, setSelectedRuntime] = useState(runtimeTargets[0]?.id ?? '')
  const [authStage, setAuthStage] = useState<AuthStage>('landing')
  const [authLoading, setAuthLoading] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)
  const [authInfo, setAuthInfo] = useState<string | null>(null)
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [pendingEmail, setPendingEmail] = useState<string | null>(null)
  const [code, setCode] = useState('')
  const [token, setToken] = useState<string | null>(() =>
    window.localStorage.getItem(TOKEN_STORAGE_KEY),
  )
  const [user, setUser] = useState<UserProfile | null>(null)
  const [dashboard, setDashboard] = useState<DashboardSnapshot | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>(() =>
    token ? 'dashboard' : 'landing',
  )
  const [showSurvey, setShowSurvey] = useState(false)
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [surveyCompleted, setSurveyCompleted] = useState(false)
  const [surveyLoading, setSurveyLoading] = useState(false)

  const activeFile = useMemo(
    () => files.find((file) => file.id === activeFileId) ?? files[0],
    [files, activeFileId],
  )

  const handleEditorChange = (value?: string) => {
    if (!activeFile || activeFile.readOnly) return

    setFiles((prev) =>
      prev.map((file) =>
        file.id === activeFile.id ? { ...file, content: value ?? '' } : file,
      ),
    )
  }

  const appendLog = (message: string, level?: ConsoleLevel) =>
    setConsoleLines((prev) => [...prev, createLog(message, level)])

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
    resetAuthStatus()
    if (stage === 'register') {
      setPendingEmail(null)
      setPassword('')
    }
  }

  const handleLoginSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setAuthLoading(true)
    resetAuthStatus()
    try {
      const data = await login({ email, password })
      window.localStorage.setItem(TOKEN_STORAGE_KEY, data.access_token)
      setToken(data.access_token)
      setUser(data.user)
      setPassword('')
      closeAuthModal()
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Не удалось войти')
    } finally {
      setAuthLoading(false)
    }
  }

  const handleRegisterSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setAuthLoading(true)
    resetAuthStatus()
    try {
      await registerUser({ email, fullName, password })
      setPendingEmail(email)
      setAuthStage('verify')
      setAuthInfo(`Мы отправили код подтверждения на ${email}.`)
      setCode('')
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Не удалось отправить код')
    } finally {
      setAuthLoading(false)
    }
  }

  const handleVerifySubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!(pendingEmail || email)) {
      setAuthError('Укажи e-mail, который использовал при регистрации')
      return
    }
    setAuthLoading(true)
    resetAuthStatus()
    try {
      await verifyRegistration({
        email: pendingEmail ?? email,
        code,
      })
      setAuthInfo('Email подтвержден. Теперь можно войти.')
      setAuthStage('login')
      setCode('')
    } catch (error) {
      setAuthError(error instanceof Error ? error.message : 'Не удалось подтвердить код')
    } finally {
      setAuthLoading(false)
    }
  }

  const renderAuthForm = () => {
    if (authStage === 'login') {
      return (
        <>
          <h2>Вход в аккаунт</h2>
          <form onSubmit={handleLoginSubmit}>
            <label>
              <span className="label-text">E-mail</span>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="your@email.com"
                required
              />
            </label>
            <label>
              <span className="label-text">Пароль</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
              />
            </label>
            <button type="submit" className="submit-btn" disabled={authLoading}>
              {authLoading ? 'Входим...' : 'Войти'}
            </button>
          </form>
          <p className="auth-hint">
            Нет аккаунта?{' '}
            <button type="button" className="link-like" onClick={() => startAuthFlow('register')}>
              Зарегистрироваться
            </button>
          </p>
        </>
      )
    }

    if (authStage === 'register') {
      return (
        <>
          <h2>Регистрация</h2>
          <form onSubmit={handleRegisterSubmit}>
            <label>
              <span className="label-text">E-mail</span>
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="your@email.com"
                required
              />
            </label>
            <label>
              <span className="label-text">Имя (необязательно)</span>
              <input
                type="text"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                placeholder="Как к тебе обращаться"
              />
            </label>
            <label>
              <span className="label-text">Пароль</span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Минимум 8 символов"
                required
                minLength={8}
              />
            </label>
            <button type="submit" className="submit-btn" disabled={authLoading}>
              {authLoading ? 'Отправляем код...' : 'Зарегистрироваться'}
            </button>
          </form>
          <p className="auth-hint">
            Уже есть аккаунт?{' '}
            <button type="button" className="link-like" onClick={() => startAuthFlow('login')}>
              Войти
            </button>
          </p>
        </>
      )
    }

    if (authStage === 'verify') {
      return (
        <>
          <h2>Подтверждение почты</h2>
          <p className="verify-info">
            Введите 6-значный код, который пришёл на{' '}
            <strong>{(pendingEmail ?? email) || 'указанный email'}</strong>
          </p>
          <form onSubmit={handleVerifySubmit} className="verify-form">
            <label>
              <span className="label-text">Код подтверждения</span>
              <input
                type="text"
                value={code}
                onChange={(event) => setCode(event.target.value)}
                minLength={6}
                maxLength={6}
                placeholder="000000"
                required
                className="code-input"
              />
            </label>
            <div className="verify-actions">
              <button type="submit" disabled={authLoading} className="submit-btn">
                {authLoading ? 'Проверяем...' : 'Подтвердить'}
              </button>
              <button
                type="button"
                className="ghost"
                onClick={() => startAuthFlow('register')}
              >
                Изменить данные
              </button>
            </div>
          </form>
        </>
      )
    }

    return null
  }

  const hydrateProfile = async (tokenValue: string) => {
    try {
      const [profile, snapshot] = await Promise.all([
        fetchProfile(tokenValue),
        fetchDashboard(tokenValue),
      ])
      setUser(profile)
      setDashboard(snapshot)
    } catch (error) {
      console.error(error)
      handleLogout()
    }
  }

  useEffect(() => {
    if (!token) {
      setUser(null)
      setDashboard(null)
      setViewMode('landing')
      return
    }
    void hydrateProfile(token).then(() => setViewMode('dashboard'))
  }, [token])

  useEffect(() => {
    if (token && viewMode === 'dashboard') {
      void loadQuestionsAndAnswers()
    }
  }, [token, viewMode])

  const loadQuestionsAndAnswers = async () => {
    if (!token) return
    try {
      // Сначала загружаем вопросы
      const questionsData = await fetchQuestions(token)
      setQuestions(questionsData)
      
      // Потом загружаем ответы
      const answersData = await fetchMyAnswers(token)
      const answersMap: Record<string, string> = {}
      answersData.forEach((answer) => {
        answersMap[answer.question_id] = answer.text
      })
      setAnswers(answersMap)
      
      // Проверяем, завершен ли опрос (все вопросы отвечены)
      if (questionsData.length > 0 && answersData.length === questionsData.length) {
        const allAnswered = questionsData.every((q) => answersMap[q.id]?.trim())
        if (allAnswered) {
          setSurveyCompleted(true)
        }
      }
    } catch (error) {
      console.error('Failed to load questions/answers:', error)
    }
  }

  // Проверяем, завершен ли опрос при изменении ответов
  useEffect(() => {
    if (questions.length > 0 && Object.keys(answers).length === questions.length) {
      const allAnswered = questions.every((q) => answers[q.id]?.trim())
      if (allAnswered && !surveyCompleted) {
        setSurveyCompleted(true)
      }
    }
  }, [answers, questions, surveyCompleted])

  const handleSubmitAnswer = async (questionId: string, text: string) => {
    if (!token) return
    try {
      setSurveyLoading(true)
      await submitAnswer(token, questionId, { question_id: questionId, text })
      setAnswers((prev) => ({ ...prev, [questionId]: text }))
      appendLog('Ответ сохранен', 'success')
    } catch (error) {
      appendLog(
        error instanceof Error ? error.message : 'Ошибка сохранения ответа',
        'error',
      )
    } finally {
      setSurveyLoading(false)
    }
  }

  const handleRunSuite = () => {
    if (!user) {
      setViewMode('landing')
      startAuthFlow('login')
      setAuthError('Сначала авторизуйся, чтобы отправлять задания.')
      return
    }
    const runtime = runtimeTargets.find((item) => item.id === selectedRuntime)
    appendLog(`Enqueued Docker job via executor (${runtime?.version ?? 'runtime'})`)
    appendLog('Queue → Redis → Executor', 'info')
  }

  const handleQuickValidation = () => {
    appendLog('Started fast tier validation (lint + smoke tests)', 'success')
  }

  const isFileActive = (fileId: string) => fileId === activeFile?.id

  const handleLogout = () => {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY)
    setToken(null)
    setUser(null)
    setDashboard(null)
    setViewMode('landing')
    setAuthStage('landing')
    resetAuthStatus()
  }

  if (viewMode === 'admin' && token) {
    return <AdminPanel token={token} onBack={() => setViewMode('dashboard')} />
  }

  if (viewMode !== 'ide') {
    return (
      <div className="screen">
        {viewMode === 'landing' && (
          <section className="landing-screen">
            <header className="landing-hero">
              <div>
                <p className="eyebrow">VibeCode Jam IDE</p>
                <h1>Создавай резюме и код в облаке</h1>
                <p className="subtitle">
                  Авторизуйся и получи доступ к IDE, опроснику для резюме и административной панели
                  для вопросов.
                </p>
                <div className="landing-actions">
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
              <div className="landing-preview">
                <div className="preview-card">
                  <p>⚡ Код запускается в Docker окружении</p>
                </div>
                <div className="preview-card">
                  <p>📋 Отвечай на вопросы и улучшай резюме</p>
                </div>
                <div className="preview-card">
                  <p>🔐 Подтверждение через код на почте</p>
                </div>
              </div>
            </header>

            {authStage !== 'landing' && (
              <div className="auth-modal" onClick={closeAuthModal}>
                <div
                  className="auth-card"
                  onClick={(event) => {
                    event.stopPropagation()
                  }}
                >
                  <button type="button" className="modal-close" onClick={closeAuthModal}>
                    ×
                  </button>
                  {renderAuthForm()}
                  {authInfo && <div className="auth-info">{authInfo}</div>}
                  {authError && (
                    <div className="auth-error">
                      <span className="error-icon">⚠️</span>
                      <span>{authError}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </section>
        )}

        {viewMode === 'dashboard' && user && (
          <section className="dashboard-screen">
            <div>
              <p className="eyebrow">
                {user.is_verified ? 'Аккаунт подтверждён' : 'Email не подтвержден'}
              </p>
              <h1>Привет, {user.full_name ?? user.email}!</h1>
              <p className="subtitle">
                Мы сохранили твои настройки и готовы запустить редактор, когда захочешь.
              </p>
              {dashboard && (
                <ul className="stats">
                  <li>
                    <span>Последний статус</span>
                    <strong>{dashboard.last_executor_status}</strong>
                  </li>
                  <li>
                    <span>Очередь</span>
                    <strong>{dashboard.pending_jobs}</strong>
                  </li>
                  <li>
                    <span>Язык</span>
                    <strong>{dashboard.last_language}</strong>
                  </li>
                </ul>
              )}
            </div>

            {!surveyCompleted && questions.length > 0 && (
              <>
                {!showSurvey ? (
                  <div className="survey-prompt">
                    <div className="survey-icon">📋</div>
                    <p>Помоги нам улучшить сервис — пройди опрос ({questions.length} вопросов)</p>
                    <div className="survey-actions">
                      <button
                        type="button"
                        className="survey-btn primary"
                        onClick={() => {
                          setShowSurvey(true)
                          setCurrentQuestionIndex(0)
                        }}
                      >
                        Пройти опрос
                      </button>
                      <button
                        type="button"
                        className="survey-btn ghost"
                        onClick={() => setSurveyCompleted(true)}
                      >
                        Пропустить
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="survey-section">
                    <div className="survey-header">
                      <h3>
                        Вопрос {currentQuestionIndex + 1} из {questions.length}
                      </h3>
                      <button
                        type="button"
                        className="close-survey"
                        onClick={() => {
                          setShowSurvey(false)
                          if (Object.keys(answers).length === questions.length) {
                            setSurveyCompleted(true)
                          }
                        }}
                        aria-label="Закрыть опрос"
                      >
                        ×
                      </button>
                    </div>
                    <div className="survey-content">
                      {currentQuestionIndex < questions.length && (
                        <>
                          <p className="survey-question">
                            {questions[currentQuestionIndex].text}
                          </p>
                          <label className="survey-text-input">
                            <span className="label-text">Ваш ответ</span>
                            <textarea
                              value={answers[questions[currentQuestionIndex].id] || ''}
                              onChange={(e) =>
                                setAnswers({
                                  ...answers,
                                  [questions[currentQuestionIndex].id]: e.target.value,
                                })
                              }
                              placeholder="Введите ваш ответ..."
                              rows={4}
                              required
                            />
                          </label>
                          <div className="survey-navigation">
                            {currentQuestionIndex > 0 && (
                              <button
                                type="button"
                                className="survey-btn ghost"
                                onClick={() => setCurrentQuestionIndex(currentQuestionIndex - 1)}
                              >
                                ← Назад
                              </button>
                            )}
                            <button
                              type="button"
                              className="survey-submit"
                              disabled={
                                !answers[questions[currentQuestionIndex].id]?.trim() ||
                                surveyLoading
                              }
                              onClick={async () => {
                                const question = questions[currentQuestionIndex]
                                const answerText = answers[question.id]
                                if (answerText?.trim()) {
                                  await handleSubmitAnswer(question.id, answerText)
                                  if (currentQuestionIndex < questions.length - 1) {
                                    setCurrentQuestionIndex(currentQuestionIndex + 1)
                                  } else {
                                    setShowSurvey(false)
                                    setSurveyCompleted(true)
                                    appendLog('Опрос завершен', 'success')
                                  }
                                }
                              }}
                            >
                              {currentQuestionIndex < questions.length - 1
                                ? 'Далее →'
                                : 'Завершить'}
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}

            <div className="dashboard-actions">
              <button type="button" className="ghost" onClick={handleLogout}>
                Выйти
              </button>
              {user?.is_admin && (
                <button
                  type="button"
                  className="admin-link-btn"
                  onClick={() => setViewMode('admin')}
                >
                  🔧 Админка
                </button>
              )}
              <button type="button" className="primary" onClick={() => setViewMode('ide')}>
                Перейти в редактор
              </button>
            </div>
          </section>
        )}
      </div>
    )
  }

  return (
    <div className="app-shell">
      <header className="top-bar">
        <div className="project-meta">
          <p className="project-name">VibeCode Jam IDE</p>
          <span className="project-branch">
            feature/runtime-split · TypeScript workspace
          </span>
        </div>
        <div className="top-bar-actions">
          {user && (
            <div className="user-chip">
              <div>
                <p>{user.full_name ?? user.email}</p>
                <span>{user.email}</span>
              </div>
              <button type="button" onClick={() => setViewMode('dashboard')}>
                Назад
              </button>
            </div>
          )}
          <button type="button" className="ghost">
            Open command palette
          </button>
          <button type="button" className="primary" onClick={handleRunSuite}>
            Run in Docker
          </button>
        </div>
      </header>

      <div className="app-body">
        <aside className="side-panel">
          {user && (
            <div className="account-card">
              <p className="panel-title">Аккаунт</p>
              <strong>{user.full_name ?? 'Безымянный разработчик'}</strong>
              <span>{user.email}</span>
              {dashboard && (
                <ul className="account-meta">
                  <li>
                    <p>Последний ран</p>
                    <span>{dashboard.last_executor_status}</span>
                  </li>
                  <li>
                    <p>В очереди</p>
                    <span>{dashboard.pending_jobs}</span>
                  </li>
                  <li>
                    <p>Язык</p>
                    <span>{dashboard.last_language}</span>
                  </li>
                </ul>
              )}
            </div>
          )}
          <div className="panel-title">Runtimes</div>
          <ul className="runtime-list">
            {runtimeTargets.map((runtime) => (
              <li key={runtime.id}>
                <label className="runtime-item">
                  <input
                    type="radio"
                    name="runtime"
                    value={runtime.id}
                    checked={selectedRuntime === runtime.id}
                    onChange={() => setSelectedRuntime(runtime.id)}
                  />
                  <div>
                    <p>{runtime.label}</p>
                    <span>{runtime.description}</span>
                  </div>
                  <code>{runtime.version}</code>
                </label>
              </li>
            ))}
          </ul>

          <div className="panel-title">Workspace</div>
          <ul className="file-tree">
            {files.map((file) => (
              <li key={file.id}>
                <button
                  type="button"
                  className={isFileActive(file.id) ? 'file active' : 'file'}
                  onClick={() => setActiveFileId(file.id)}
                >
                  <div>
                    <p>{file.name}</p>
                    <span>{file.path}</span>
                  </div>
                  <span className="lang-chip">{file.language}</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <section className="workspace">
          <div className="tabs">
            {files.map((file) => (
              <button
                key={file.id}
                type="button"
                className={isFileActive(file.id) ? 'tab active' : 'tab'}
                onClick={() => setActiveFileId(file.id)}
              >
                {file.name}
                {file.readOnly && <span className="readonly-indicator">ro</span>}
              </button>
            ))}
          </div>

          <div className="editor-surface">
            {activeFile ? (
              <Editor
                language={activeFile.language}
                theme="vs-dark"
                value={activeFile.content}
                onChange={handleEditorChange}
                height="100%"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  smoothScrolling: true,
                  readOnly: !!activeFile.readOnly,
                  scrollBeyondLastLine: false,
                }}
              />
            ) : (
              <div className="empty-state">No file selected</div>
            )}
          </div>

          <div className="bottom-panels">
            <section className="panel console">
              <header>
                <div>
                  <p>Console</p>
                  <span>Executor & DAP stream</span>
                </div>
                <button type="button" onClick={handleQuickValidation}>
                  Quick test
                </button>
              </header>

              <ul className="console-log">
                {consoleLines.map((line) => (
                  <li key={line.id} className={line.level}>
                    <span className="timestamp">{line.timestamp}</span>
                    <span className="message">{line.message}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="panel tests">
              <header>
                <div>
                  <p>Fast tier</p>
                  <span>Runs on backend w/o containers</span>
                </div>
              </header>
              <ul className="test-list">
                {quickTests.map((test) => (
                  <li key={test.id} className={test.status}>
      <div>
                      <p>{test.name}</p>
                      <span>{test.durationMs ? `${test.durationMs}ms` : 'queued'}</span>
                    </div>
                    <span className="status-pill">{test.status}</span>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        </section>
      </div>

    </div>
  )
}

export default App

import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { LandingPage } from './pages/LandingPage'
import { HomePage } from './pages/HomePage'
import { SelectVacancyPage } from './pages/SelectVacancyPage'
import { VacanciesPage } from './pages/VacanciesPage'
import { VacancyDetailPage } from './pages/VacancyDetailPage'
import { SurveyPage } from './pages/SurveyPage'
import { SurveyCompletePage } from './pages/SurveyCompletePage'
import { DashboardPage } from './pages/DashboardPage'
import { IdePage } from './pages/IdePage'
import { AdminPage } from './pages/AdminPage'
import { ModeratorPage } from './pages/ModeratorPage'
import { ContestCompletePage } from './pages/ContestCompletePage'
import './App.css'

const TOKEN_STORAGE_KEY = 'vibecode_token'

function App() {
  const navigate = useNavigate()
  const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)

  useEffect(() => {
    // Если нет токена и пользователь не на landing, admin или moderator, перенаправляем на главную
    const currentPath = window.location.pathname
    // Разрешаем доступ к публичным страницам без токена
    const publicPaths = ['/', '/admin', '/moderator']
    if (!token && !publicPaths.includes(currentPath)) {
      navigate('/')
    }
  }, [token, navigate])

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/home"
        element={token ? <HomePage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/select-vacancy"
        element={token ? <SelectVacancyPage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/vacancies"
        element={token ? <VacanciesPage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/vacancy/:vacancyId"
        element={token ? <VacancyDetailPage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/survey"
        element={token ? <SurveyPage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/survey-complete"
        element={token ? <SurveyCompletePage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/dashboard"
        element={token ? <DashboardPage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/ide"
        element={token ? <IdePage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/contest/:vacancyId"
        element={token ? <IdePage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/contest-complete"
        element={token ? <ContestCompletePage /> : <Navigate to="/" replace />}
      />
      <Route
        path="/admin"
        element={<AdminPage />}
      />
      <Route
        path="/moderator"
        element={<ModeratorPage />}
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App

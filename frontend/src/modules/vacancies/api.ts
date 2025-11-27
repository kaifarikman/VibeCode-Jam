import type { Vacancy, Application } from './types'
import type { Question } from '../questions/types'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000/api'

const buildUrl = (path: string) => `${API_BASE_URL}${path}`

const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
})

export async function fetchVacancies(
  token: string,
  language?: string,
  grade?: string,
): Promise<Vacancy[]> {
  const params = new URLSearchParams()
  if (language) params.append('language', language)
  if (grade) params.append('grade', grade)

  const response = await fetch(buildUrl(`/vacancies?${params.toString()}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить вакансии')
  }
  return (await response.json()) as Vacancy[]
}

export async function fetchVacancy(token: string, id: string): Promise<Vacancy> {
  const response = await fetch(buildUrl(`/vacancies/${id}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить вакансию')
  }
  return (await response.json()) as Vacancy
}

export async function applyToVacancy(
  token: string,
  vacancyId: string,
): Promise<{ application: Application; isNew: boolean }> {
  const response = await fetch(buildUrl(`/vacancies/${vacancyId}/apply`), {
    method: 'POST',
    headers: getAuthHeaders(token),
  })
  
  // Принимаем как 200 (уже существует), так и 201 (создана новая)
  if (response.status === 200 || response.status === 201) {
    const application = (await response.json()) as Application
    const isNew = response.status === 201
    return { application, isNew }
  }
  
  // Обрабатываем ошибки
  const error = await response.json().catch(() => ({ detail: 'Ошибка подачи заявки' }))
  throw new Error(error.detail || 'Не удалось подать заявку')
}

export async function getMyApplications(token: string): Promise<Application[]> {
  const response = await fetch(buildUrl('/vacancies/my/applications'), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить заявки')
  }
  return (await response.json()) as Application[]
}

export async function getSurveyQuestions(
  token: string,
  vacancyId: string,
): Promise<Question[]> {
  const response = await fetch(buildUrl(`/vacancies/${vacancyId}/survey-questions`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки вопросов' }))
    throw new Error(error.detail || 'Не удалось загрузить вопросы')
  }
  return (await response.json()) as Question[]
}

export async function updateApplicationStatus(
  token: string,
  applicationId: string,
  status: string,
): Promise<Application> {
  const response = await fetch(
    buildUrl(`/vacancies/applications/${applicationId}/status`),
    {
      method: 'PATCH',
      headers: getAuthHeaders(token),
      body: JSON.stringify({ status }),
    }
  )
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка обновления статуса' }))
    throw new Error(error.detail || 'Не удалось обновить статус')
  }
  return (await response.json()) as Application
}

export async function getRandomTasks(
  token: string,
  vacancyId: string,
): Promise<Question[]> {
  const response = await fetch(buildUrl(`/vacancies/${vacancyId}/tasks`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки задач' }))
    throw new Error(error.detail || 'Не удалось загрузить задачи')
  }
  return (await response.json()) as Question[]
}


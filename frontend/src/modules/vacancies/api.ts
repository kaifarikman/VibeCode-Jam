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
  try {
    const params = new URLSearchParams()
    if (language) params.append('language', language)
    if (grade) params.append('grade', grade)

    const url = params.toString() 
      ? buildUrl(`/vacancies?${params.toString()}`)
      : buildUrl('/vacancies')
    
    const response = await fetch(url, {
      headers: getAuthHeaders(token),
    })
    
    if (!response.ok) {
      let errorMessage = 'Не удалось загрузить вакансии'
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        // Если не удалось распарсить JSON, используем статус код
        if (response.status === 401) {
          errorMessage = 'Требуется авторизация'
        } else if (response.status === 500) {
          errorMessage = 'Ошибка сервера при загрузке вакансий'
        }
      }
      throw new Error(errorMessage)
    }
    
    const data = await response.json()
    return data as Vacancy[]
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Неожиданная ошибка при загрузке вакансий')
  }
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
  try {
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
    let errorMessage = 'Не удалось подать заявку'
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch {
      if (response.status === 400) {
        errorMessage = 'Неверный запрос'
      } else if (response.status === 401) {
        errorMessage = 'Требуется авторизация'
      } else if (response.status === 404) {
        errorMessage = 'Вакансия не найдена'
      } else if (response.status === 500) {
        errorMessage = 'Ошибка сервера при подаче заявки'
      }
    }
    throw new Error(errorMessage)
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Неожиданная ошибка при подаче заявки')
  }
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
  try {
    const response = await fetch(buildUrl(`/vacancies/${vacancyId}/survey-questions`), {
      headers: getAuthHeaders(token),
    })
    
    if (!response.ok) {
      let errorMessage = 'Не удалось загрузить вопросы'
      try {
        const errorData = await response.json()
        errorMessage = errorData.detail || errorData.message || errorMessage
      } catch {
        // Если не удалось распарсить JSON, используем статус код
        if (response.status === 404) {
          errorMessage = 'Вакансия не найдена'
        } else if (response.status === 400) {
          errorMessage = 'Нет вопросов для этой вакансии'
        } else if (response.status === 401) {
          errorMessage = 'Требуется авторизация'
        } else if (response.status === 500) {
          errorMessage = 'Ошибка сервера при загрузке вопросов'
        }
      }
      throw new Error(errorMessage)
    }
    
    const data = await response.json()
    return data as Question[]
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Неожиданная ошибка при загрузке вопросов')
  }
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


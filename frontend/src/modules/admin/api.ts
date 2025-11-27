import type {
  Question,
  QuestionCreate,
  QuestionUpdate,
  Vacancy,
  VacancyCreate,
  VacancyUpdate,
} from './types'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000/api'

const buildUrl = (path: string) => `${API_BASE_URL}${path}`

const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
})

export async function fetchQuestions(token: string): Promise<Question[]> {
  const response = await fetch(buildUrl('/admin/questions'), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить вопросы')
  }
  return (await response.json()) as Question[]
}

export async function createQuestion(
  token: string,
  data: QuestionCreate,
): Promise<Question> {
  const response = await fetch(buildUrl('/admin/questions'), {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка создания вопроса' }))
    throw new Error(error.detail || 'Не удалось создать вопрос')
  }
  return (await response.json()) as Question
}

export async function updateQuestion(
  token: string,
  id: string,
  data: QuestionUpdate,
): Promise<Question> {
  const response = await fetch(buildUrl(`/admin/questions/${id}`), {
    method: 'PUT',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка обновления вопроса' }))
    throw new Error(error.detail || 'Не удалось обновить вопрос')
  }
  return (await response.json()) as Question
}

export async function deleteQuestion(token: string, id: string): Promise<void> {
  const response = await fetch(buildUrl(`/admin/questions/${id}`), {
    method: 'DELETE',
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось удалить вопрос')
  }
}

// Vacancies API
export async function fetchVacancies(token: string): Promise<Vacancy[]> {
  const response = await fetch(buildUrl('/admin/vacancies'), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить вакансии')
  }
  return (await response.json()) as Vacancy[]
}

export async function createVacancy(
  token: string,
  data: VacancyCreate,
): Promise<Vacancy> {
  const response = await fetch(buildUrl('/admin/vacancies'), {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка создания вакансии' }))
    throw new Error(error.detail || 'Не удалось создать вакансию')
  }
  return (await response.json()) as Vacancy
}

export async function updateVacancy(
  token: string,
  id: string,
  data: VacancyUpdate,
): Promise<Vacancy> {
  const response = await fetch(buildUrl(`/admin/vacancies/${id}`), {
    method: 'PUT',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка обновления вакансии' }))
    throw new Error(error.detail || 'Не удалось обновить вакансию')
  }
  return (await response.json()) as Vacancy
}

export async function deleteVacancy(token: string, id: string): Promise<void> {
  const response = await fetch(buildUrl(`/admin/vacancies/${id}`), {
    method: 'DELETE',
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось удалить вакансию')
  }
}

// Tasks API
import type { Task, TaskCreate, TaskUpdate } from '../tasks/types'

export async function fetchTasks(token: string): Promise<Task[]> {
  const response = await fetch(buildUrl('/admin/tasks'), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить задачи')
  }
  return (await response.json()) as Task[]
}

export async function createTask(
  token: string,
  data: TaskCreate,
): Promise<Task> {
  const response = await fetch(buildUrl('/admin/tasks'), {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка создания задачи' }))
    throw new Error(error.detail || 'Не удалось создать задачу')
  }
  return (await response.json()) as Task
}

export async function updateTask(
  token: string,
  id: string,
  data: TaskUpdate,
): Promise<Task> {
  const response = await fetch(buildUrl(`/admin/tasks/${id}`), {
    method: 'PUT',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка обновления задачи' }))
    throw new Error(error.detail || 'Не удалось обновить задачу')
  }
  return (await response.json()) as Task
}

export async function deleteTask(token: string, id: string): Promise<void> {
  const response = await fetch(buildUrl(`/admin/tasks/${id}`), {
    method: 'DELETE',
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось удалить задачу')
  }
}


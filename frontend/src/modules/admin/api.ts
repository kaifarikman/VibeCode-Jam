import type { Question, QuestionCreate, QuestionUpdate } from './types'

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


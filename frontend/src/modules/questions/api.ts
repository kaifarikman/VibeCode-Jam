import type { Answer, AnswerCreate, AnswerWithQuestion, Question } from './types'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000/api'

const buildUrl = (path: string) => `${API_BASE_URL}${path}`

const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
})

export async function fetchQuestions(token: string): Promise<Question[]> {
  const response = await fetch(buildUrl('/questions'), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить вопросы')
  }
  return (await response.json()) as Question[]
}

export async function fetchQuestion(token: string, id: string): Promise<Question> {
  const response = await fetch(buildUrl(`/questions/${id}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить вопрос')
  }
  return (await response.json()) as Question
}

export async function submitAnswer(
  token: string,
  questionId: string,
  data: AnswerCreate,
): Promise<Answer> {
  const response = await fetch(buildUrl(`/questions/${questionId}/answers`), {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка сохранения ответа' }))
    throw new Error(error.detail || 'Не удалось сохранить ответ')
  }
  return (await response.json()) as Answer
}

export async function fetchMyAnswers(token: string): Promise<AnswerWithQuestion[]> {
  const response = await fetch(buildUrl('/questions/me/answers'), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить ответы')
  }
  return (await response.json()) as AnswerWithQuestion[]
}


import type { Task, TaskCreate, TaskUpdate, TestCase } from './types'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000/api'

const buildUrl = (path: string) => `${API_BASE_URL}${path}`

const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
})

export async function fetchContestTasks(
  token: string,
  vacancyId: string,
): Promise<Task[]> {
  const response = await fetch(buildUrl(`/tasks/contest/${vacancyId}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки задач' }))
    throw new Error(error.detail || 'Не удалось загрузить задачи')
  }
  return (await response.json()) as Task[]
}

export async function fetchTask(token: string, taskId: string): Promise<Task> {
  const response = await fetch(buildUrl(`/tasks/${taskId}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки задачи' }))
    throw new Error(error.detail || 'Не удалось загрузить задачу')
  }
  return (await response.json()) as Task
}

export async function fetchTaskTestsForSubmit(
  token: string,
  taskId: string,
): Promise<{ open_tests: TestCase[] | null; hidden_tests: TestCase[] | null }> {
  const response = await fetch(buildUrl(`/tasks/${taskId}/tests-for-submit`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки тестов' }))
    throw new Error(error.detail || 'Не удалось загрузить тесты')
  }
  return (await response.json()) as { open_tests: TestCase[] | null; hidden_tests: TestCase[] | null }
}

export async function fetchSolvedTasks(
  token: string,
  vacancyId: string,
): Promise<string[]> {
  const response = await fetch(buildUrl(`/tasks/solved/${vacancyId}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки решенных задач' }))
    throw new Error(error.detail || 'Не удалось загрузить решенные задачи')
  }
  return (await response.json()) as string[]
}


import type { Execution, ExecutionRequest, ExecutionResult } from './types'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000/api'

const buildUrl = (path: string) => `${API_BASE_URL}${path}`

const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
})

export async function createExecution(
  token: string,
  data: ExecutionRequest,
): Promise<Execution> {
  const response = await fetch(buildUrl('/executions'), {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(data),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка создания задачи' }))
    throw new Error(error.detail || 'Не удалось создать задачу на выполнение')
  }
  return (await response.json()) as Execution
}

export async function getExecution(token: string, id: string): Promise<Execution> {
  const response = await fetch(buildUrl(`/executions/${id}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось получить информацию о выполнении')
  }
  return (await response.json()) as Execution
}

export async function listExecutions(token: string, limit = 20): Promise<Execution[]> {
  const response = await fetch(buildUrl(`/executions?limit=${limit}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    throw new Error('Не удалось получить список выполнений')
  }
  return (await response.json()) as Execution[]
}


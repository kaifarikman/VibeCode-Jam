const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000/api'

const buildUrl = (path: string) => `${API_BASE_URL}${path}`

const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
})

export interface HintRequest {
  task_id: string
  hint_level: 'surface' | 'medium' | 'deep'
}

export interface HintResponse {
  content: string
  penalty: number
  remaining_hints: number
}

export async function requestHint(
  token: string,
  request: HintRequest,
): Promise<HintResponse> {
  const response = await fetch(buildUrl('/hints/request'), {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify(request),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка запроса подсказки' }))
    throw new Error(error.detail || 'Не удалось получить подсказку')
  }
  return (await response.json()) as HintResponse
}

export async function getUsedHints(
  token: string,
  taskId: string,
): Promise<string[]> {
  const response = await fetch(buildUrl(`/hints/used/${taskId}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки подсказок' }))
    throw new Error(error.detail || 'Не удалось загрузить использованные подсказки')
  }
  return (await response.json()) as string[]
}

export async function getAvailableHints(
  token: string,
  taskId: string,
): Promise<string[]> {
  const response = await fetch(buildUrl(`/hints/available/${taskId}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки доступных подсказок' }))
    throw new Error(error.detail || 'Не удалось загрузить доступные подсказки')
  }
  return (await response.json()) as string[]
}


import type {
  Task,
  TaskCreate,
  TaskUpdate,
  TestCase,
  SolutionMlMeta,
  SolutionAntiCheatMeta,
  TaskCommunication,
} from './types'

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

export interface LastSolution {
  solution_code: string | null
  language: string | null
  status?: string
  verdict?: string | null
  updated_at?: string
  ml?: SolutionMlMeta | null
  anti_cheat?: SolutionAntiCheatMeta | null
}

export async function fetchLastSolution(
  token: string,
  taskId: string,
  vacancyId?: string,
): Promise<LastSolution> {
  const url = new URL(buildUrl(`/tasks/${taskId}/last-solution`))
  if (vacancyId) {
    url.searchParams.append('vacancy_id', vacancyId)
  }
  const response = await fetch(url.toString(), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки решения' }))
    throw new Error(error.detail || 'Не удалось загрузить решение')
  }
  return (await response.json()) as LastSolution
}

export interface ContestCompletionStatus {
  all_solved: boolean
  total_tasks: number
  solved_tasks: number
  task_ids: string[]
}

export async function fetchContestCompletionStatus(
  token: string,
  vacancyId: string,
): Promise<ContestCompletionStatus> {
  const response = await fetch(buildUrl(`/tasks/contest/${vacancyId}/completion-status`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка проверки статуса' }))
    throw new Error(error.detail || 'Не удалось проверить статус завершения')
  }
  return (await response.json()) as ContestCompletionStatus
}

export async function fetchTaskCommunication(
  token: string,
  taskId: string,
): Promise<TaskCommunication | null> {
  const response = await fetch(buildUrl(`/tasks/${taskId}/communication`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки чата' }))
    throw new Error(error.detail || 'Не удалось загрузить чат')
  }
  const data = await response.json()
  return data as TaskCommunication | null
}

export async function answerTaskCommunication(
  token: string,
  taskId: string,
  answer: string,
): Promise<TaskCommunication> {
  const response = await fetch(buildUrl(`/tasks/${taskId}/communication/answer`), {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify({ answer }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка отправки ответа' }))
    throw new Error(error.detail || 'Не удалось отправить ответ')
  }
  return (await response.json()) as TaskCommunication
}


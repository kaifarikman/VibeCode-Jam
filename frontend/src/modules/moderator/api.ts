import type { Application } from '../vacancies/types'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000/api'

const buildUrl = (path: string) => `${API_BASE_URL}${path}`

const getAuthHeaders = (token: string) => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${token}`,
})

export interface ApplicationDetail {
  application: {
    id: string
    user_id: string
    user_email: string
    user_full_name: string | null
    vacancy_id: string
    vacancy_title: string
    vacancy_position: string
    status: string
    ml_score: number | null
    created_at: string
    updated_at: string
  }
  task_solutions: Array<{
    task_id: string
    task_title: string
    task_description: string
    solution_code: string
    language: string
    status: string
    verdict: string | null
    test_results: any
    created_at: string
    metric: {
      tests_total: number | null
      tests_passed: number | null
      total_duration_ms: number | null
      average_duration_ms: number | null
      verdict: string | null
      language: string
    } | null
  }>
  survey_answers: Array<{
    question_id: string
    question_text: string
    answer_text: string
    created_at: string
  }>
}

export async function fetchApplicationsForModeration(token: string): Promise<Application[]> {
  const response = await fetch(buildUrl('/moderator/applications'), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки заявок' }))
    throw new Error(error.detail || 'Не удалось загрузить заявки')
  }
  return (await response.json()) as Application[]
}

export async function fetchApplicationDetails(
  token: string,
  applicationId: string,
): Promise<ApplicationDetail> {
  const response = await fetch(buildUrl(`/moderator/applications/${applicationId}`), {
    headers: getAuthHeaders(token),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка загрузки деталей заявки' }))
    throw new Error(error.detail || 'Не удалось загрузить детали заявки')
  }
  return (await response.json()) as ApplicationDetail
}

export async function decideApplication(
  token: string,
  applicationId: string,
  decision: 'accepted' | 'rejected',
  comment?: string,
): Promise<{ success: boolean; application_id: string; new_status: string; decision: string }> {
  const response = await fetch(buildUrl(`/moderator/applications/${applicationId}/decide`), {
    method: 'POST',
    headers: getAuthHeaders(token),
    body: JSON.stringify({ decision, comment }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка принятия решения' }))
    throw new Error(error.detail || 'Не удалось принять решение')
  }
  return (await response.json()) as { success: boolean; application_id: string; new_status: string; decision: string }
}


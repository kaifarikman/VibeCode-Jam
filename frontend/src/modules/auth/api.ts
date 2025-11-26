import type {
  AuthSuccessResponse,
  DashboardSnapshot,
  LoginPayload,
  RegisterPayload,
  UserProfile,
  VerifyCodePayload,
} from './types'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') ?? 'http://localhost:8000/api'

const buildUrl = (path: string) => `${API_BASE_URL}${path}`

const jsonHeaders = {
  'Content-Type': 'application/json',
}

export async function registerUser(payload: RegisterPayload) {
  const response = await fetch(buildUrl('/auth/register'), {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify({
      email: payload.email,
      full_name: payload.fullName,
      password: payload.password,
    }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Не удалось отправить код' }))
    throw new Error(error.detail || 'Не удалось отправить код подтверждения')
  }
  return response.json()
}

export async function verifyRegistration(payload: VerifyCodePayload) {
  const response = await fetch(buildUrl('/auth/verify'), {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Код недействителен' }))
    throw new Error(error.detail || 'Код недействителен или истёк')
  }
  return response.json()
}

export async function login(payload: LoginPayload) {
  const response = await fetch(buildUrl('/auth/login'), {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка входа' }))
    throw new Error(error.detail || 'Неверный email или пароль')
  }
  return (await response.json()) as AuthSuccessResponse
}

export async function fetchProfile(token: string) {
  const response = await fetch(buildUrl('/users/me'), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  if (!response.ok) {
    throw new Error('Не удалось получить профиль')
  }
  return (await response.json()) as UserProfile
}

export async function fetchDashboard(token: string) {
  const response = await fetch(buildUrl('/users/me/dashboard'), {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
  if (!response.ok) {
    throw new Error('Не удалось загрузить дашборд')
  }
  return (await response.json()) as DashboardSnapshot
}


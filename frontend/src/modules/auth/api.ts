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
    const errorData = await response.json().catch(() => ({ detail: 'Не удалось отправить код' }))
    
    // Обработка ошибок валидации (422)
    if (response.status === 422 && errorData.detail) {
      if (Array.isArray(errorData.detail)) {
        // Pydantic validation errors
        const messages = errorData.detail.map((err: any) => {
          const field = err.loc?.[err.loc.length - 1] || 'поле'
          const msg = err.msg || 'Ошибка валидации'
          return `${field === 'body' ? '' : field + ': '}${msg}`
        })
        throw new Error(messages.join('. ') || 'Ошибка валидации данных')
      }
      throw new Error(errorData.detail || 'Ошибка валидации данных')
    }
    
    // Обработка других ошибок
    const errorMessage = errorData.detail || 
      (response.status === 400 ? 'Неверные данные для регистрации' :
       response.status === 500 ? 'Ошибка сервера. Попробуйте позже' :
       'Не удалось отправить код подтверждения')
    throw new Error(errorMessage)
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
    const errorData = await response.json().catch(() => ({ detail: 'Код недействителен' }))
    
    // Обработка ошибок валидации (422)
    if (response.status === 422 && errorData.detail) {
      if (Array.isArray(errorData.detail)) {
        const messages = errorData.detail.map((err: any) => {
          const field = err.loc?.[err.loc.length - 1] || 'поле'
          const msg = err.msg || 'Ошибка валидации'
          return `${field === 'body' ? '' : field + ': '}${msg}`
        })
        throw new Error(messages.join('. ') || 'Ошибка валидации данных')
      }
      throw new Error(errorData.detail || 'Ошибка валидации данных')
    }
    
    const errorMessage = errorData.detail || 
      (response.status === 400 ? 'Неверный код подтверждения' :
       response.status === 500 ? 'Ошибка сервера. Попробуйте позже' :
       'Код недействителен или истёк')
    throw new Error(errorMessage)
  }
  return (await response.json()) as AuthSuccessResponse
}

export async function login(payload: LoginPayload) {
  const response = await fetch(buildUrl('/auth/login'), {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Ошибка входа' }))
    
    // Обработка ошибок валидации (422)
    if (response.status === 422 && errorData.detail) {
      if (Array.isArray(errorData.detail)) {
        const messages = errorData.detail.map((err: any) => {
          const field = err.loc?.[err.loc.length - 1] || 'поле'
          const msg = err.msg || 'Ошибка валидации'
          return `${field === 'body' ? '' : field + ': '}${msg}`
        })
        throw new Error(messages.join('. ') || 'Ошибка валидации данных')
      }
      throw new Error(errorData.detail || 'Ошибка валидации данных')
    }
    
    const errorMessage = errorData.detail || 
      (response.status === 400 ? 'Неверный email или пароль' :
       response.status === 500 ? 'Ошибка сервера. Попробуйте позже' :
       'Ошибка входа')
    throw new Error(errorMessage)
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

export async function requestLoginCode(payload: { email: string }) {
  const response = await fetch(buildUrl('/auth/request-code'), {
    method: 'POST',
    headers: jsonHeaders,
    body: JSON.stringify({ email: payload.email }),
  })
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Ошибка отправки кода' }))
    throw new Error(error.detail || 'Не удалось отправить код')
  }
  return response.json()
}


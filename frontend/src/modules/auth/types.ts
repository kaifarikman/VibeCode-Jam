export type AuthStage = 'landing' | 'login' | 'register' | 'verify'

export type RegisterPayload = {
  email: string
  fullName?: string
  password: string
}

export type LoginPayload = {
  email: string
  password: string
}

export type VerifyCodePayload = {
  email: string
  code: string
}

export type UserProfile = {
  id: string
  email: string
  full_name: string | null
  is_admin: boolean
  is_verified: boolean
  created_at: string
  last_login_at: string | null
}

export type DashboardSnapshot = {
  last_executor_status: string
  pending_jobs: number
  last_language: string
  recent_actions: string[]
}

export type AuthSuccessResponse = {
  access_token: string
  token_type: string
  user: UserProfile
}


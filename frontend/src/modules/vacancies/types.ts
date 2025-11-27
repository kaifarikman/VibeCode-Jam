export type Vacancy = {
  id: string
  title: string
  position: string
  language: string
  grade: string
  ideal_resume: string
  created_at: string
  updated_at: string
}

export type Application = {
  id: string
  user_id: string
  vacancy_id: string
  ml_score: number | null
  status: 'pending' | 'survey_completed' | 'algo_test_completed' | 'final_verdict'
  created_at: string
  updated_at: string
  vacancy?: Vacancy | null  // Информация о вакансии
}


export type Question = {
  id: string
  text: string
  order: number
  question_type: string
  options: string | null
  difficulty?: string
  vacancy_id?: string | null
  created_at: string
  updated_at: string
}

export type QuestionCreate = {
  text: string
  order?: number
  question_type?: string
  options?: string | null
  difficulty?: string
  vacancy_id?: string | null
}

export type QuestionUpdate = {
  text?: string
  order?: number
  question_type?: string
  options?: string | null
  difficulty?: string
  vacancy_id?: string | null
}

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

export type VacancyCreate = {
  title: string
  position: string
  language: string
  grade: string
  ideal_resume: string
}

export type VacancyUpdate = {
  title?: string
  position?: string
  language?: string
  grade?: string
  ideal_resume?: string
}


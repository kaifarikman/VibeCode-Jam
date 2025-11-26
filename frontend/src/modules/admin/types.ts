export type Question = {
  id: string
  text: string
  order: number
  created_at: string
  updated_at: string
}

export type QuestionCreate = {
  text: string
  order?: number
}

export type QuestionUpdate = {
  text?: string
  order?: number
}


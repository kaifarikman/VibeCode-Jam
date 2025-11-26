export type Question = {
  id: string
  text: string
  order: number
  created_at: string
  updated_at: string
}

export type Answer = {
  id: string
  user_id: string
  question_id: string
  text: string
  created_at: string
  updated_at: string
}

export type AnswerCreate = {
  question_id: string
  text: string
}

export type AnswerWithQuestion = {
  id: string
  user_id: string
  question_id: string
  text: string
  created_at: string
  updated_at: string
  question: Question
}


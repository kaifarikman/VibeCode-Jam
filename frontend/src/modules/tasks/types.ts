export type TestCase = {
  input: string
  output: string
}

export type Task = {
  id: string
  title: string
  description: string
  topic: string | null
  difficulty: 'easy' | 'medium' | 'hard'
  open_tests: TestCase[] | null
  hidden_tests: TestCase[] | null  // Только для админки
  vacancy_id: string | null
  created_at: string
  updated_at: string
  canonical_solution?: string | null
}

export type TaskCreate = {
  title: string
  description: string
  topic: string | null
  difficulty: 'easy' | 'medium' | 'hard'
  open_tests: TestCase[] | null
  hidden_tests: TestCase[] | null
  vacancy_id: string | null
  canonical_solution?: string | null
}

export type TaskUpdate = {
  title?: string
  description?: string
  topic?: string | null
  difficulty?: 'easy' | 'medium' | 'hard'
  open_tests?: TestCase[] | null
  hidden_tests?: TestCase[] | null
  vacancy_id?: string | null
  canonical_solution?: string | null
}

export type TaskGenerateRequest = {
  difficulty: 'easy' | 'medium' | 'hard'
  topic?: string | null
  vacancy_id?: string | null
}


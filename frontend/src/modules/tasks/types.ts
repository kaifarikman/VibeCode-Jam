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
  language?: string | null
}

export type SolutionMlMeta = {
  correctness?: number | null
  efficiency?: number | null
  clean_code?: number | null
  feedback?: string | null
  passed?: boolean | null
}

export type SolutionAntiCheatMeta = {
  flag?: boolean | null
  reason?: string | null
}

export type TaskCommunication = {
  id: string
  task_id: string
  vacancy_id: string | null
  solution_id: string
  question: string
  answer: string | null
  status: 'pending' | 'evaluating' | 'completed' | 'error'
  ml_score?: number | null
  ml_feedback?: string | null
  created_at: string
  updated_at: string
}


export type TestCase = {
  input: string
  output: string
}

export type ExecutionRequest = {
  language: string
  files: Record<string, string>
  timeout?: number
  test_cases?: TestCase[]
  task_id?: string
  vacancy_id?: string
  is_submit?: boolean
}

export type TestResult = {
  test_index: number
  input: string
  expected_output: string
  actual_output: string
  passed: boolean
  duration_ms: number
}

export type ExecutionResult = {
  stdout: string
  stderr: string
  exit_code: number
  duration_ms: number
  verdict?: string
  test_results?: TestResult[]
}

export type Execution = {
  id: string
  user_id: string
  language: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  files: Record<string, string>
  result: ExecutionResult | null
  error_message: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}


import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { fetchProfile } from '../modules/auth/api'
import type { UserProfile } from '../modules/auth/types'
import { codeSamples, getSolutionFileName } from '../modules/ide/codeSamples'
import { fetchQuestions } from '../modules/questions/api'
import { getRandomTasks, fetchVacancy } from '../modules/vacancies/api'
import {
  fetchContestTasks,
  fetchSolvedTasks,
  fetchTaskTestsForSubmit,
  fetchLastSolution,
  fetchContestCompletionStatus,
  fetchTaskCommunication,
  answerTaskCommunication,
} from '../modules/tasks/api'
import type { Question } from '../modules/questions/types'
import type { Task, TaskCommunication, SolutionMlMeta, SolutionAntiCheatMeta } from '../modules/tasks/types'
import { createExecution, getExecution } from '../modules/executions/api'
import type { Execution } from '../modules/executions/types'
import { requestHint, getUsedHints, getAvailableHints, type HintResponse } from '../modules/hints/api'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import remarkBreaks from 'remark-breaks'
import type { PluggableList } from 'unified'
import '../App.css'

const TOKEN_STORAGE_KEY = 'vibecode_token'
const LANGUAGE_STORAGE_KEY = 'vibecode_language'
type SupportedLanguage = 'python' | 'typescript' | 'go' | 'java'

const normalizeLanguage = (value?: string | null): SupportedLanguage => {
  const lang = (value || '').toLowerCase()
  if (lang.startsWith('py')) return 'python'
  if (lang.startsWith('ts') || lang.includes('type')) return 'typescript'
  if (lang.startsWith('go')) return 'go'
  if (lang.startsWith('java')) return 'java'
  return 'python'
}

const languageLabels: Record<SupportedLanguage, string> = {
  python: 'Python',
  typescript: 'TypeScript',
  go: 'Go',
  java: 'Java',
}


export function IdePage() {
  const navigate = useNavigate()
  const params = useParams()
  const [searchParams] = useSearchParams()
  const vacancyId = searchParams.get('vacancy_id')
  const taskIdsParam = searchParams.get('task_ids')
  const contestVacancyId = params.vacancyId || searchParams.get('contest_vacancy_id') || null
  
  const [user, setUser] = useState<UserProfile | null>(null)
  const [selectedLanguage, setSelectedLanguage] = useState<SupportedLanguage>(() => {
    const saved = window.localStorage.getItem(LANGUAGE_STORAGE_KEY) as SupportedLanguage
    return saved || 'python'
  })
  const [contestLanguage, setContestLanguage] = useState<SupportedLanguage | null>(null)
  const [contestCompleted, setContestCompleted] = useState(false)
  const [solutionCode, setSolutionCode] = useState<string>(() => {
    // В контестном режиме всегда начинаем с пустого шаблона
    // Проверяем, есть ли contest_vacancy_id в URL
    const urlParams = new URLSearchParams(window.location.search)
    const hasContest = urlParams.get('contest_vacancy_id') || window.location.pathname.includes('/contest/')
    if (hasContest) {
      return codeSamples[selectedLanguage] || codeSamples.python
    }
    const saved = window.localStorage.getItem(`solution_${selectedLanguage}`)
    return saved || codeSamples[selectedLanguage] || codeSamples.python
  })
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null)
  const [questions, setQuestions] = useState<Question[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [isContestMode, setIsContestMode] = useState(false)
  const [solvedTaskIds, setSolvedTaskIds] = useState<Set<string>>(new Set())
  const [currentExecution, setCurrentExecution] = useState<Execution | null>(null)
  const [executionLoading, setExecutionLoading] = useState(false)
  const [runMode, setRunMode] = useState<'run' | 'submit'>('run') // 'run' для открытых тестов, 'submit' для всех
  const [activeTab, setActiveTab] = useState<'condition' | 'solution' | 'results' | 'chat'>('condition')
  const [usedHints, setUsedHints] = useState<Set<string>>(new Set()) // Использованные подсказки для текущей задачи
  const [availableHints, setAvailableHints] = useState<string[]>([]) // Доступные подсказки
  const [hintLoading, setHintLoading] = useState(false)
  const [currentHint, setCurrentHint] = useState<HintResponse | null>(null) // Текущая открытая подсказка
  const [totalPenalty, setTotalPenalty] = useState(0) // Общий штраф за подсказки
  const [lastSolutionMeta, setLastSolutionMeta] = useState<{
    ml: SolutionMlMeta | null
    antiCheat: SolutionAntiCheatMeta | null
  } | null>(null)
  const [communication, setCommunication] = useState<TaskCommunication | null>(null)
  const [communicationAnswer, setCommunicationAnswer] = useState('')
  const [communicationLoading, setCommunicationLoading] = useState(false)
  const [communicationError, setCommunicationError] = useState<string | null>(null)
  const effectiveLanguage: SupportedLanguage = (isContestMode && contestLanguage) ? contestLanguage : selectedLanguage
  const markdownPlugins = useMemo<PluggableList>(
    () => [
      remarkGfm as PluggableList[number],
      remarkBreaks as unknown as PluggableList[number],
    ],
    [],
  )

  useEffect(() => {
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) {
      navigate('/')
      return
    }
    void loadUser(token)
    
    // Если есть contest_vacancy_id, загружаем задачи для контеста
    if (contestVacancyId) {
      void loadContestTasks(token, contestVacancyId)
    } else if (vacancyId && taskIdsParam) {
      // Если есть vacancy_id и task_ids, загружаем задачи по ID (старый режим)
      void loadTasksByIds(token, vacancyId, taskIdsParam)
    } else if (vacancyId) {
      // Если только vacancy_id, загружаем случайные задачи (старый режим)
      void loadRandomTasks(token, vacancyId)
    } else {
      // Иначе загружаем все вопросы (старый режим)
      void loadQuestions(token)
    }
  }, [navigate, vacancyId, taskIdsParam, contestVacancyId])

  const loadLastSolutionData = useCallback(
    async (
      taskId: string,
      options?: { vacancyId?: string | null; applyCode?: boolean; lockLanguage?: boolean },
    ) => {
      const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
      if (!token || !taskId) return
      try {
        const lastSolution = await fetchLastSolution(token, taskId, options?.vacancyId ?? undefined)
        setLastSolutionMeta({
          ml: lastSolution.ml ?? null,
          antiCheat: lastSolution.anti_cheat ?? null,
        })
        if (options?.applyCode) {
          if (lastSolution.solution_code && lastSolution.language) {
            setSolutionCode(lastSolution.solution_code)
            if (
              lastSolution.language !== selectedLanguage &&
              ['python', 'typescript', 'go', 'java'].includes(lastSolution.language)
            ) {
              setSelectedLanguage(lastSolution.language as SupportedLanguage)
            }
          } else {
            setSolutionCode(codeSamples[selectedLanguage] || codeSamples.python)
          }
        }
        if (
          options?.lockLanguage &&
          lastSolution.language &&
          ['python', 'typescript', 'go', 'java'].includes(lastSolution.language)
        ) {
          const normalized = normalizeLanguage(lastSolution.language)
          setContestLanguage(normalized)
          setSelectedLanguage(normalized)
        }
        return lastSolution
      } catch (error) {
        console.error('Failed to load last solution:', error)
        if (options?.applyCode) {
          setSolutionCode(codeSamples[selectedLanguage] || codeSamples.python)
        }
      }
    },
    [selectedLanguage],
  )

  const loadCommunicationForTask = useCallback(async (taskId: string): Promise<TaskCommunication | null> => {
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token || !taskId) return null
    try {
      const data = await fetchTaskCommunication(token, taskId)
      setCommunication(data)
      setCommunicationAnswer(data?.answer ?? '')
      setCommunicationError(null)
      return data
    } catch (error) {
      console.error('Failed to load communication:', error)
      setCommunication(null)
      setCommunicationAnswer('')
      setCommunicationError(error instanceof Error ? error.message : 'Не удалось загрузить чат')
      return null
    }
  }, [])

  // Загружаем подсказки, решение и чат при смене задачи
  useEffect(() => {
    if (!selectedTaskId) {
      setLastSolutionMeta(null)
      setCommunication(null)
      setCommunicationAnswer('')
      return
    }
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) {
      navigate('/')
      return
    }
    if (isContestMode) {
      void loadHintsForTask(token, selectedTaskId)
      setCurrentHint(null)
      setCurrentExecution(null)
      setActiveTab('condition')
    }
    void loadLastSolutionData(selectedTaskId, {
      vacancyId: contestVacancyId,
      applyCode: isContestMode,
      lockLanguage: isContestMode,
    })
    void loadCommunicationForTask(selectedTaskId)
  }, [
    selectedTaskId,
    isContestMode,
    contestVacancyId,
    navigate,
    loadLastSolutionData,
    loadCommunicationForTask,
  ])

  const loadUser = async (token: string) => {
    try {
      const profile = await fetchProfile(token)
      setUser(profile)
    } catch (error) {
      console.error('Failed to load user:', error)
      navigate('/')
    }
  }

  const loadQuestions = async (token: string) => {
    try {
      const questionsData = await fetchQuestions(token)
      setQuestions(questionsData)
      if (questionsData.length > 0) {
        const sorted = [...questionsData].sort((a, b) => a.order - b.order)
        setSelectedTaskId(sorted[0].id)
      }
    } catch (error) {
      console.error('Failed to load questions:', error)
    }
  }

  const loadContestTasks = async (token: string, vacancyId: string) => {
    try {
      setIsContestMode(true)
      setContestCompleted(false)
      let forcedLanguage: SupportedLanguage = normalizeLanguage(selectedLanguage)
      try {
        const vacancy = await fetchVacancy(token, vacancyId)
        forcedLanguage = normalizeLanguage(vacancy.language)
        setContestLanguage(forcedLanguage)
      } catch (error) {
        console.error('Failed to load vacancy info for contest', error)
        setContestLanguage(forcedLanguage)
      }
      setSelectedLanguage(forcedLanguage)
      // Сбрасываем код на шаблон при входе в контестный режим
      setSolutionCode(codeSamples[forcedLanguage] || codeSamples.python)
      const contestTasks = await fetchContestTasks(token, vacancyId)
      setTasks(contestTasks)
      if (contestTasks.length > 0) {
        setSelectedTaskId(contestTasks[0].id)
      }
      
      // Загружаем решенные задачи
      try {
        const solvedIds = await fetchSolvedTasks(token, vacancyId)
        const solvedSet = new Set(solvedIds)
        setSolvedTaskIds(solvedSet)
        if (contestTasks.length > 0) {
          const everySolved = contestTasks.every(task => solvedSet.has(task.id))
          setContestCompleted(everySolved)
        }
      } catch (error) {
        console.error('Failed to load solved tasks:', error)
        // Не критично, продолжаем работу
      }
    } catch (error) {
      console.error('Failed to load contest tasks:', error)
    }
  }

  const handleCommunicationSubmit = async () => {
    if (!communication || !selectedTaskId || !communicationAnswer.trim()) {
      return
    }
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) {
      navigate('/')
      return
    }
    setCommunicationLoading(true)
    setCommunicationError(null)
    try {
      const response = await answerTaskCommunication(token, selectedTaskId, communicationAnswer.trim())
      setCommunication(response)
      setCommunicationAnswer(response.answer ?? '')
    } catch (error) {
      console.error('Failed to send communication answer:', error)
      setCommunicationError(error instanceof Error ? error.message : 'Не удалось отправить ответ')
    } finally {
      setCommunicationLoading(false)
    }
  }

  const formatScore = (value?: number | null) => {
    if (value === undefined || value === null) {
      return '—'
    }
    return `${Math.round(value * 100)}%`
  }

  // Загрузить использованные и доступные подсказки для задачи
  const loadHintsForTask = async (token: string, taskId: string) => {
    if (!isContestMode || !taskId) return
    
    try {
      const [used, available] = await Promise.all([
        getUsedHints(token, taskId),
        getAvailableHints(token, taskId),
      ])
      setUsedHints(new Set(used))
      setAvailableHints(available)
      
      // Вычисляем общий штраф
      const penalties: Record<string, number> = { surface: 5, medium: 15, deep: 30 }
      const penalty = used.reduce((sum, level) => sum + (penalties[level] || 0), 0)
      setTotalPenalty(penalty)
    } catch (error) {
      console.error('Failed to load hints:', error)
    }
  }

  // Запросить подсказку
  const handleRequestHint = async (hintLevel: 'surface' | 'medium' | 'deep') => {
    if (!selectedTaskId || !user || hintLoading) return
    
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token) return
    
    setHintLoading(true)
    try {
      const response = await requestHint(token, {
        task_id: selectedTaskId,
        hint_level: hintLevel,
      })
      
      setCurrentHint(response)
      setUsedHints(prev => new Set([...prev, hintLevel]))
      setAvailableHints(prev => prev.filter(level => level !== hintLevel))
      setTotalPenalty(prev => prev + response.penalty)
    } catch (error) {
      console.error('Failed to request hint:', error)
      alert(error instanceof Error ? error.message : 'Не удалось получить подсказку')
    } finally {
      setHintLoading(false)
    }
  }

  const loadRandomTasks = async (token: string, vacancyId: string) => {
    try {
      const tasks = await getRandomTasks(token, vacancyId)
      setQuestions(tasks)
      if (tasks.length > 0) {
        setSelectedTaskId(tasks[0].id)
      }
    } catch (error) {
      console.error('Failed to load random tasks:', error)
      // Fallback на обычную загрузку вопросов
      void loadQuestions(token)
    }
  }

  const loadTasksByIds = async (token: string, vacancyId: string, taskIds: string) => {
    try {
      // Получаем все вопросы и фильтруем по переданным ID
      const allQuestions = await fetchQuestions(token)
      const taskIdsArray = taskIds.split(',')
      const orderedTasks = taskIdsArray
        .map(id => allQuestions.find(q => q.id === id))
        .filter((task): task is Question => task !== undefined)
      
      if (orderedTasks.length > 0) {
        setQuestions(orderedTasks)
        setSelectedTaskId(orderedTasks[0].id)
      } else {
        // Fallback на случайные задачи для вакансии
        void loadRandomTasks(token, vacancyId)
      }
    } catch (error) {
      console.error('Failed to load tasks by IDs:', error)
      // Fallback на случайные задачи для вакансии
      if (vacancyId) {
        void loadRandomTasks(token, vacancyId)
      } else {
        void loadQuestions(token)
      }
    }
  }

  useEffect(() => {
    // В контестном режиме не сохраняем код в localStorage
    if (!isContestMode && solutionCode) {
      window.localStorage.setItem(`solution_${selectedLanguage}`, solutionCode)
    }
  }, [solutionCode, selectedLanguage, isContestMode])

  useEffect(() => {
    if (isContestMode) {
      return
    }
    const saved = window.localStorage.getItem(`solution_${selectedLanguage}`)
    if (saved) {
      setSolutionCode(saved)
    } else {
      setSolutionCode(codeSamples[selectedLanguage] || codeSamples.python)
    }
  }, [selectedLanguage, isContestMode])

  const allContestSolved = useMemo(() => {
    if (!isContestMode || tasks.length === 0) return false
    return tasks.every(task => solvedTaskIds.has(task.id))
  }, [isContestMode, tasks, solvedTaskIds])

  useEffect(() => {
    if (allContestSolved) {
      setContestCompleted(true)
    }
  }, [allContestSolved])

  const selectedTask = useMemo(() => {
    if (!selectedTaskId) return null
    if (isContestMode) {
      return tasks.find((t) => t.id === selectedTaskId) || null
    }
    return questions.find((q) => q.id === selectedTaskId) || null
  }, [questions, tasks, selectedTaskId, isContestMode])

  const taskDescription = useMemo(() => {
    if (!selectedTask) return ''
    if (isContestMode && 'description' in selectedTask) {
      return selectedTask.description ?? ''
    }
    if ('text' in selectedTask) {
      return selectedTask.text ?? ''
    }
    return ''
  }, [selectedTask, isContestMode])

  const contestReady = isContestMode && (contestCompleted || allContestSolved)


  const handleEditorChange = (value?: string) => {
    setSolutionCode(value || '')
  }

  const handleLanguageChange = (lang: SupportedLanguage) => {
    if (isContestMode && contestLanguage) {
      return
    }
    setSelectedLanguage(lang)
    window.localStorage.setItem(LANGUAGE_STORAGE_KEY, lang)
  }

  const handleRunSuite = async () => {
    const token = window.localStorage.getItem(TOKEN_STORAGE_KEY)
    if (!token || !user) {
      navigate('/')
      return
    }

    if (!selectedTaskId) {
      return
    }

    const solutionFileName = getSolutionFileName(effectiveLanguage)
    const filesToSend: Record<string, string> = {
      [solutionFileName]: solutionCode,
    }

    // Если режим контеста и выбрана задача, получаем тесты
    let testCases: Array<{ input: string; output: string }> | undefined = undefined
    if (isContestMode && selectedTask && 'open_tests' in selectedTask && selectedTaskId) {
      if (runMode === 'run' && selectedTask.open_tests) {
        // "Запустить" - только открытые тесты
        testCases = selectedTask.open_tests.map(tc => ({ input: tc.input, output: tc.output }))
      } else if (runMode === 'submit') {
        // "Submit" - все тесты (открытые + закрытые)
        // Запрашиваем все тесты для Submit
        try {
          const testsData = await fetchTaskTestsForSubmit(token, selectedTaskId)
          const allTests: Array<{ input: string; output: string }> = []
          
          // Добавляем открытые тесты
          if (testsData.open_tests) {
            allTests.push(...testsData.open_tests.map(tc => ({ input: tc.input, output: tc.output })))
          }
          
          // Добавляем закрытые тесты
          if (testsData.hidden_tests) {
            allTests.push(...testsData.hidden_tests.map(tc => ({ input: tc.input, output: tc.output })))
          }
          
          testCases = allTests.length > 0 ? allTests : undefined
        } catch (error) {
          console.error('Failed to fetch tests for submit:', error)
          setExecutionLoading(false)
          return
        }
      }
    }

    try {
      setExecutionLoading(true)

      const execution = await createExecution(token, {
        language: effectiveLanguage,
        files: filesToSend,
        timeout: 30,
        test_cases: testCases,
        task_id: isContestMode && selectedTaskId ? selectedTaskId : undefined,
        vacancy_id: contestVacancyId ? contestVacancyId : undefined,
        is_submit: runMode === 'submit',
      })

      setCurrentExecution(execution)
      
      // Переключаемся на вкладку результатов при запуске
      setActiveTab('results')

      // Сохраняем runMode и другие параметры для использования в pollExecutionStatus
      const currentRunMode = runMode
      const currentTaskId = selectedTaskId
      const currentVacancyId = contestVacancyId
      pollExecutionStatus(execution.id, token, currentRunMode, currentTaskId, currentVacancyId)
    } catch (error) {
      console.error('Execution error:', error)
      setExecutionLoading(false)
    }
  }

  const pollExecutionStatus = async (
    executionId: string,
    token: string,
    currentRunMode: 'run' | 'submit' = 'run',
    currentTaskId: string | null = null,
    currentVacancyId: string | null = null,
    maxAttempts = 60
  ) => {
    let attempts = 0
    const pollInterval = 1000

    const poll = async () => {
      if (attempts >= maxAttempts) {
        setExecutionLoading(false)
        return
      }

      try {
        const execution = await getExecution(token, executionId)
        setCurrentExecution(execution)

        if (execution.status === 'completed') {
          setExecutionLoading(false)
          
          // Если это Submit, всегда перезагружаем список решенных задач
          // Это гарантирует, что мы получим актуальное состояние с сервера
          if (
            currentRunMode === 'submit' &&
            currentTaskId &&
            currentVacancyId
          ) {
            // Небольшая задержка, чтобы backend успел сохранить решение
            setTimeout(async () => {
              try {
                const solvedIds = await fetchSolvedTasks(token, currentVacancyId)
                setSolvedTaskIds(new Set(solvedIds))
                console.log('Reloaded solved tasks:', solvedIds)
                
                // Если задача решена (по вердикту или по списку с сервера), добавляем локально
                const isAccepted = execution.result?.verdict === 'ACCEPTED' || solvedIds.includes(currentTaskId)
                if (isAccepted) {
                  setSolvedTaskIds(prev => new Set([...prev, currentTaskId]))
                }
                
                // Проверяем, все ли задачи решены
                if (currentVacancyId) {
                  try {
                    const completionStatus = await fetchContestCompletionStatus(token, currentVacancyId)
                    setContestCompleted(completionStatus.all_solved)
                  } catch (error) {
                    console.error('Failed to check completion status:', error)
                  }
                }
              } catch (error) {
                console.error('Failed to reload solved tasks:', error)
                // Если не удалось загрузить с сервера, но вердикт ACCEPTED, добавляем локально
                if (execution.result?.verdict === 'ACCEPTED') {
                  setSolvedTaskIds(prev => new Set([...prev, currentTaskId]))
                }
              }
            }, 500) // Задержка 500ms для гарантии сохранения на backend
          }
          const isAccepted =
            currentRunMode === 'submit' &&
            currentTaskId &&
            execution.result?.verdict === 'ACCEPTED'
          if (currentTaskId) {
            void loadLastSolutionData(currentTaskId, {
              vacancyId: currentVacancyId ?? undefined,
              applyCode: false,
            })
            const requestCommunication = (attempt = 0) => {
              void loadCommunicationForTask(currentTaskId).then(comm => {
                if (comm && isAccepted) {
                  setActiveTab('chat')
                } else if (!comm && isAccepted && attempt < 3) {
                  setTimeout(() => requestCommunication(attempt + 1), 800)
                }
              })
            }
            requestCommunication()
          }
          
          return
        }

        if (execution.status === 'failed') {
          setExecutionLoading(false)
          return
        }

        attempts++
        setTimeout(poll, pollInterval)
      } catch (error) {
        console.error('Polling error:', error)
        setExecutionLoading(false)
      }
    }

    setTimeout(poll, pollInterval)
  }

  return (
    <div className="app-shell">
      <header className="top-bar">
        <div className="project-meta">
          <p className="project-name">FutureCareers IDE</p>
          <span className="project-branch">
            {selectedTask
              ? 'order' in selectedTask && selectedTask.order
                ? `Задача #${selectedTask.order}`
                : 'title' in selectedTask && selectedTask.title
                  ? selectedTask.title
                  : 'text' in selectedTask
                    ? selectedTask.text.slice(0, 40)
                    : 'Текущая задача'
              : 'Выберите задачу'}
          </span>
        </div>
        <div className="top-bar-actions">
          <div className="language-selector">
            <label htmlFor="language-select">Язык:</label>
            <select
              id="language-select"
              value={effectiveLanguage}
              onChange={(e) => handleLanguageChange(e.target.value as SupportedLanguage)}
              className="language-select"
              disabled={isContestMode && !!contestLanguage}
            >
              <option value="python">Python</option>
              <option value="typescript">TypeScript</option>
              <option value="go">Go</option>
              <option value="java">Java</option>
            </select>
            {isContestMode && contestLanguage && (
              <span className="language-locked">🔒 {languageLabels[contestLanguage]}</span>
            )}
          </div>
          {user && (
            <div className="user-chip">
              <div>
                <p>{user.full_name ?? user.email}</p>
                <span>{user.email}</span>
              </div>
              <button type="button" onClick={() => navigate('/home')}>
                Назад
              </button>
            </div>
          )}
          {isContestMode ? (
            <>
              <button
                type="button"
                className={runMode === 'run' ? 'primary' : 'secondary'}
                onClick={() => {
                  setRunMode('run')
                  void handleRunSuite()
                }}
                disabled={executionLoading || !user || !selectedTaskId}
              >
                {executionLoading && runMode === 'run'
                  ? 'Выполняется...'
                  : currentExecution?.status === 'running' && runMode === 'run'
                    ? 'Выполняется...'
                    : 'Запустить'}
              </button>
              <button
                type="button"
                className={runMode === 'submit' ? 'primary' : 'secondary'}
                onClick={() => {
                  setRunMode('submit')
                  void handleRunSuite()
                }}
                disabled={executionLoading || !user || !selectedTaskId}
              >
                {executionLoading && runMode === 'submit'
                  ? 'Отправка...'
                  : currentExecution?.status === 'running' && runMode === 'submit'
                    ? 'Отправка...'
                    : 'Submit'}
              </button>
            </>
          ) : (
            <button
              type="button"
              className="primary"
              onClick={handleRunSuite}
              disabled={executionLoading || !user || !selectedTaskId}
            >
              {executionLoading
                ? 'Выполняется...'
                : currentExecution?.status === 'running'
                  ? 'Выполняется...'
                  : 'Запустить решение'}
            </button>
          )}
        </div>
      </header>

      <div className="app-body ide-layout">
        <aside className="tasks-panel">
          <div className="panel-title">Задачи</div>
          {isContestMode ? (
            tasks.length === 0 ? (
              <div className="empty-state">Загрузка задач...</div>
            ) : (
              <ul className="tasks-list">
                {tasks.map((task, index) => (
                  <li key={task.id}>
                    <button
                      type="button"
                      className={selectedTaskId === task.id ? 'task-item active' : 'task-item'}
                      onClick={() => setSelectedTaskId(task.id)}
                    >
                      <span className="task-number">
                        #{index + 1}
                        {task.difficulty && (
                          <span className="task-difficulty" title={`Сложность: ${task.difficulty}`}>
                            {' '}({task.difficulty})
                          </span>
                        )}
                      </span>
                      <span className="task-preview">
                        {task.title || task.description.slice(0, 50)}
                        {(task.title || task.description).length > 50 ? '...' : ''}
                        {solvedTaskIds.has(task.id) && (
                          <span className="task-solved-icon" title="Задача решена"> ✓</span>
                        )}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )
          ) : questions.length === 0 ? (
            <div className="empty-state">Загрузка задач...</div>
          ) : (
            <ul className="tasks-list">
              {questions.map((question, index) => (
                <li key={question.id}>
                  <button
                    type="button"
                    className={selectedTaskId === question.id ? 'task-item active' : 'task-item'}
                    onClick={() => setSelectedTaskId(question.id)}
                  >
                    <span className="task-number">
                      {vacancyId ? `#${index + 1}` : `#${question.order}`}
                      {question.difficulty && (
                        <span className="task-difficulty" title={`Сложность: ${question.difficulty}`}>
                          {' '}({question.difficulty})
                        </span>
                      )}
                    </span>
                    <span className="task-preview">
                      {question.text.slice(0, 50)}
                      {question.text.length > 50 ? '...' : ''}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </aside>

        {/* Правая панель с вкладками */}
        <section className="right-panel">
          <div className="tabs-container">
            <div className="tabs-header">
              <button
                type="button"
                className={`tab-button ${activeTab === 'condition' ? 'active' : ''}`}
                onClick={() => setActiveTab('condition')}
              >
                Условие
              </button>
              <button
                type="button"
                className={`tab-button ${activeTab === 'solution' ? 'active' : ''}`}
                onClick={() => setActiveTab('solution')}
              >
                Решение
              </button>
              <button
                type="button"
                className={`tab-button ${activeTab === 'results' ? 'active' : ''}`}
                onClick={() => setActiveTab('results')}
              >
                Результаты
              </button>
              <button
                type="button"
                className={`tab-button ${activeTab === 'chat' ? 'active' : ''}`}
                onClick={() => setActiveTab('chat')}
              >
                Чат
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'condition' && (
                <div className="task-description">
                  {selectedTask ? (
                    <>
                      <div className="task-header">
                        <h2>
                          {isContestMode && 'title' in selectedTask
                            ? selectedTask.title
                            : `Задача #${'order' in selectedTask ? selectedTask.order : '?'}`}
                        </h2>
                        {isContestMode && 'difficulty' in selectedTask && selectedTask.difficulty && (
                          <span className="task-difficulty-badge">{selectedTask.difficulty}</span>
                        )}
                      </div>
                      <div className="task-content">
                        <div className="task-markdown">
                          <ReactMarkdown remarkPlugins={markdownPlugins}>
                            {taskDescription || '_Описание задачи пока недоступно._'}
                          </ReactMarkdown>
                        </div>
                        {/* Блок подсказок - всегда показываем в режиме контеста */}
                        {isContestMode && selectedTaskId && (
                          <div className="hints-section">
                            <div className="hints-header">
                              <h3>Подсказки</h3>
                              <div className="hints-score">
                                <span className="max-score">Максимум: 100 баллов</span>
                                {totalPenalty > 0 && (
                                  <span className="penalty">Штраф: -{totalPenalty} баллов</span>
                                )}
                                <span className="final-score">
                                  Итого: {Math.max(0, 100 - totalPenalty)} баллов
                                </span>
                              </div>
                            </div>
                            <div className="hints-buttons">
                              <button
                                type="button"
                                className={`hint-button ${usedHints.has('surface') ? 'used' : ''} ${availableHints.includes('surface') ? 'available' : ''}`}
                                onClick={() => handleRequestHint('surface')}
                                disabled={hintLoading || usedHints.has('surface')}
                                title={usedHints.has('surface') ? 'Подсказка уже использована (-5 баллов)' : 'Поверхностная подсказка (-5 баллов)'}
                              >
                                {usedHints.has('surface') ? '✓ Использована' : 'Подсказка 1'}
                                <span className="hint-penalty">-5</span>
                              </button>
                              <button
                                type="button"
                                className={`hint-button ${usedHints.has('medium') ? 'used' : ''} ${availableHints.includes('medium') ? 'available' : ''}`}
                                onClick={() => handleRequestHint('medium')}
                                disabled={hintLoading || usedHints.has('medium')}
                                title={usedHints.has('medium') ? 'Подсказка уже использована (-15 баллов)' : 'Средняя подсказка (-15 баллов)'}
                              >
                                {usedHints.has('medium') ? '✓ Использована' : 'Подсказка 2'}
                                <span className="hint-penalty">-15</span>
                              </button>
                              <button
                                type="button"
                                className={`hint-button ${usedHints.has('deep') ? 'used' : ''} ${availableHints.includes('deep') ? 'available' : ''}`}
                                onClick={() => handleRequestHint('deep')}
                                disabled={hintLoading || usedHints.has('deep')}
                                title={usedHints.has('deep') ? 'Подсказка уже использована (-30 баллов)' : 'Глубокая подсказка (-30 баллов)'}
                              >
                                {usedHints.has('deep') ? '✓ Использована' : 'Подсказка 3'}
                                <span className="hint-penalty">-30</span>
                              </button>
                            </div>
                            {currentHint && (
                              <div className="hint-content">
                                <div className="hint-content-header">
                                  <strong>Подсказка:</strong>
                                  <span className="hint-penalty-badge">-{currentHint.penalty} баллов</span>
                                </div>
                                <div className="hint-text">{currentHint.content}</div>
                                <div className="hint-footer">
                                  Осталось подсказок: {currentHint.remaining_hints}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                        {isContestMode &&
                          'open_tests' in selectedTask &&
                          selectedTask.open_tests &&
                          selectedTask.open_tests.length > 0 && (
                            <div className="task-tests">
                              <h3>Открытые тесты:</h3>
                              {selectedTask.open_tests.map((test, idx) => (
                                <div key={idx} className="test-case">
                                  <div className="test-input">
                                    <strong>Вход:</strong>
                                    <pre>{test.input}</pre>
                                  </div>
                                  <div className="test-output">
                                    <strong>Выход:</strong>
                                    <pre>{test.output}</pre>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                      </div>
                    </>
                  ) : (
                    <div className="empty-state">Выберите задачу из списка слева</div>
                  )}
                </div>
              )}

              {activeTab === 'solution' && (
                <div className="code-editor-panel">
                  <div className="editor-header">
                    <span className="editor-filename">{getSolutionFileName(effectiveLanguage)}</span>
                  </div>
                  <div className="editor-surface">
                    <Editor
                      language={effectiveLanguage === 'typescript' ? 'typescript' : effectiveLanguage}
                      theme="vs-dark"
                      value={solutionCode}
                      onChange={handleEditorChange}
                      height="100%"
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        smoothScrolling: true,
                        scrollBeyondLastLine: false,
                      }}
                    />
                  </div>
                </div>
              )}

              {activeTab === 'results' && (
                <div className="execution-results-panel">
                  <div className="results-header">
                    <h3>Результаты выполнения</h3>
                    <span>Вывод программы и вердикты</span>
                  </div>
                  {contestReady && contestVacancyId && (
                    <div className="contest-finish-banner">
                      <div>
                        <h4>Все задачи выполнены</h4>
                        <p>Ваша заявка отправлена на модерацию. Можно вернуться в главное меню.</p>
                      </div>
                      <div className="contest-finish-actions">
                        <button
                          type="button"
                          className="primary"
                          onClick={() => navigate('/home')}
                        >
                          В главное меню
                        </button>
                        <button
                          type="button"
                          className="contest-ghost"
                          onClick={() => navigate(`/contest-complete?vacancy_id=${contestVacancyId}`)}
                        >
                          Посмотреть статус
                        </button>
                      </div>
                    </div>
                  )}

                  {currentExecution && (
                    <div className="execution-results">
                      <div className={`execution-status ${currentExecution.status}`}>
                        {currentExecution.status === 'pending' && '⏳ Ожидание'}
                        {currentExecution.status === 'running' && '🔄 Выполняется'}
                        {currentExecution.status === 'completed' && '✅ Завершено'}
                        {currentExecution.status === 'failed' && '❌ Ошибка'}
                      </div>

                      {currentExecution.result && (
                        <>
                          {currentExecution.result.stdout && (
                            <div>
                              <strong style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.7)' }}>
                                Стандартный вывод:
                              </strong>
                              <div className="execution-result-output stdout">
                                {currentExecution.result.stdout}
                              </div>
                            </div>
                          )}
                          {currentExecution.result.stderr && 
                           currentExecution.result.stderr.trim() !== '' &&
                           currentExecution.result.exit_code !== 0 &&
                           !currentExecution.result.stderr.includes('Вердикт:') && (
                            <div style={{ marginTop: '12px' }}>
                              <strong style={{ fontSize: '12px', color: '#f44336' }}>
                                Ошибки:
                              </strong>
                              <div className="execution-result-output stderr">
                                {currentExecution.result.stderr}
                              </div>
                            </div>
                          )}
                          <div className="execution-meta">
                            <span>
                              Код возврата: <strong>{currentExecution.result.exit_code}</strong>
                            </span>
                            <span>
                              Время: <strong>{currentExecution.result.duration_ms}ms</strong>
                            </span>
                          </div>
                        </>
                      )}

                      {currentExecution.error_message && (
                        <div className="execution-result-output stderr">
                          {currentExecution.error_message}
                        </div>
                      )}

                      {lastSolutionMeta?.ml && (
                        <div className="result-card">
                          <div className="result-card-header">
                            <h4>Оценка кода (ML)</h4>
                            {typeof lastSolutionMeta.ml.passed === 'boolean' && (
                              <span className={`badge ${lastSolutionMeta.ml.passed ? 'success' : 'danger'}`}>
                                {lastSolutionMeta.ml.passed ? 'Оценка пройдена' : 'Требует доработки'}
                              </span>
                            )}
                          </div>
                          <div className="ml-score-grid">
                            <div>
                              <span>Корректность</span>
                              <strong>{formatScore(lastSolutionMeta.ml.correctness)}</strong>
                            </div>
                            <div>
                              <span>Эффективность</span>
                              <strong>{formatScore(lastSolutionMeta.ml.efficiency)}</strong>
                            </div>
                            <div>
                              <span>Чистота кода</span>
                              <strong>{formatScore(lastSolutionMeta.ml.clean_code)}</strong>
                            </div>
                          </div>
                          {lastSolutionMeta.ml.feedback && (
                            <p className="result-card-feedback">{lastSolutionMeta.ml.feedback}</p>
                          )}
                        </div>
                      )}

                      {lastSolutionMeta?.antiCheat &&
                        (typeof lastSolutionMeta.antiCheat.flag === 'boolean' ||
                          lastSolutionMeta.antiCheat.reason) && (
                          <div className="result-card">
                            <div className="result-card-header">
                              <h4>Проверка на плагиат</h4>
                              <span
                                className={`badge ${
                                  lastSolutionMeta.antiCheat.flag ? 'danger' : 'success'
                                }`}
                              >
                                {lastSolutionMeta.antiCheat.flag ? 'Подозрение' : 'Все чисто'}
                              </span>
                            </div>
                            {lastSolutionMeta.antiCheat.reason && (
                              <p className="result-card-feedback">{lastSolutionMeta.antiCheat.reason}</p>
                            )}
                          </div>
                        )}
                    </div>
                  )}

                </div>
              )}

              {activeTab === 'chat' && (
                <div className="chat-panel">
                  {communicationError && (
                    <div className="chat-error">
                      {communicationError}
                    </div>
                  )}

                  {!communication && !communicationError && (
                    <div className="empty-state">Вопрос появится после успешного Submit.</div>
                  )}

                  {communication && (
                    <>
                      <div className="chat-question">
                        <h3>Вопрос от системы</h3>
                        <div className="chat-markdown">
                          <ReactMarkdown remarkPlugins={markdownPlugins}>
                            {communication.question}
                          </ReactMarkdown>
                        </div>
                      </div>
                      <div className="chat-status-row">
                        <span
                          className={`badge ${
                            communication.status === 'completed'
                              ? 'success'
                              : communication.status === 'pending'
                                ? 'warning'
                                : communication.status === 'error'
                                  ? 'danger'
                                  : 'info'
                          }`}
                        >
                          {communication.status === 'pending' && 'Ждёт вашего ответа'}
                          {communication.status === 'evaluating' && 'Оцениваем ответ'}
                          {communication.status === 'completed' && 'Оценено'}
                          {communication.status === 'error' && 'Ошибка оценки'}
                        </span>
                        {typeof communication.ml_score === 'number' && (
                          <span className="chat-score">
                            Оценка: {Math.round(communication.ml_score * 100)} / 100
                          </span>
                        )}
                      </div>

                      {communication.status === 'pending' && (
                        <div className="chat-input">
                          <textarea
                            value={communicationAnswer}
                            onChange={(e) => setCommunicationAnswer(e.target.value)}
                            placeholder="Опишите ход мыслей, объясните решение, укажите ограничения..."
                            rows={5}
                            disabled={communicationLoading}
                          />
                          <button
                            type="button"
                            className="chat-send-button primary"
                            onClick={handleCommunicationSubmit}
                            disabled={communicationLoading || !communicationAnswer.trim()}
                          >
                            {communicationLoading ? 'Отправка...' : 'Отправить'}
                          </button>
                        </div>
                      )}

                      {communication.status === 'evaluating' && (
                        <p className="field-hint">Мы оцениваем ваш ответ, подождите пару секунд...</p>
                      )}

                      {communication.status === 'completed' && (
                        <div className="chat-answer-view">
                          <strong>Ваш ответ</strong>
                          <div className="chat-markdown">
                            <ReactMarkdown remarkPlugins={markdownPlugins}>
                              {communication.answer || '—'}
                            </ReactMarkdown>
                          </div>
                          {communication.ml_feedback && (
                            <div className="chat-markdown field-hint">
                              <ReactMarkdown remarkPlugins={markdownPlugins}>
                                {communication.ml_feedback}
                              </ReactMarkdown>
                            </div>
                          )}
                        </div>
                      )}

                      {communication.status === 'error' && (
                        <p className="field-hint">
                          Не удалось получить оценку от ML сервиса. Ответ сохранён, попробуйте позже.
                        </p>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}


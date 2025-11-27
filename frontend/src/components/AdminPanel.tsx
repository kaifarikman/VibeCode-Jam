import { type FormEvent, useEffect, useState } from 'react'
import {
  createQuestion,
  createTask,
  createVacancy,
  deleteQuestion,
  deleteTask,
  deleteVacancy,
  fetchQuestions,
  fetchTasks,
  fetchVacancies,
  updateQuestion,
  updateTask,
  updateVacancy,
} from '../modules/admin/api'
import type {
  Question,
  QuestionCreate,
  QuestionUpdate,
  Vacancy,
  VacancyCreate,
  VacancyUpdate,
} from '../modules/admin/types'
import type { Task, TaskCreate, TaskUpdate } from '../modules/tasks/types'
import './AdminPanel.css'

interface AdminPanelProps {
  token: string
}

type Tab = 'questions' | 'vacancies' | 'tasks'

export function AdminPanel({ token }: AdminPanelProps) {
  const [activeTab, setActiveTab] = useState<Tab>('questions')
  const [questions, setQuestions] = useState<Question[]>([])
  const [vacancies, setVacancies] = useState<Vacancy[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingQuestionId, setEditingQuestionId] = useState<string | null>(null)
  const [editingVacancyId, setEditingVacancyId] = useState<string | null>(null)
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null)
  const [showQuestionForm, setShowQuestionForm] = useState(false)
  const [showVacancyForm, setShowVacancyForm] = useState(false)
  const [showTaskForm, setShowTaskForm] = useState(false)
  const [questionFormData, setQuestionFormData] = useState<QuestionCreate>({
    text: '',
    order: 0,
    question_type: 'text',
    options: null,
    difficulty: 'medium',
  })
  const [vacancyFormData, setVacancyFormData] = useState<VacancyCreate>({
    title: '',
    position: '',
    language: 'python',
    grade: 'junior',
    ideal_resume: '',
  })
  const [taskFormData, setTaskFormData] = useState<TaskCreate>({
    title: '',
    description: '',
    topic: null,
    difficulty: 'medium',
    open_tests: [],
    hidden_tests: [],
    vacancy_id: null,
  })

  useEffect(() => {
    void loadData()
  }, [activeTab])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      if (activeTab === 'questions') {
        const data = await fetchQuestions(token)
        setQuestions(data)
      } else if (activeTab === 'vacancies') {
        const data = await fetchVacancies(token)
        setVacancies(data)
      } else if (activeTab === 'tasks') {
        const data = await fetchTasks(token)
        setTasks(data)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки данных')
    } finally {
      setLoading(false)
    }
  }

  // Questions handlers
  const handleCreateQuestion = async (event: FormEvent) => {
    event.preventDefault()
    try {
      setError(null)
      await createQuestion(token, questionFormData)
      setQuestionFormData({ text: '', order: 0, question_type: 'text', options: null, difficulty: 'medium', vacancy_id: null })
      setShowQuestionForm(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания вопроса')
    }
  }

  const handleUpdateQuestion = async (id: string, data: QuestionUpdate) => {
    try {
      setError(null)
      await updateQuestion(token, id, data)
      setEditingQuestionId(null)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления вопроса')
    }
  }

  const handleDeleteQuestion = async (id: string) => {
    if (!confirm('Вы уверены, что хотите удалить этот вопрос?')) {
      return
    }
    try {
      setError(null)
      await deleteQuestion(token, id)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления вопроса')
    }
  }

  // Vacancies handlers
  const handleCreateVacancy = async (event: FormEvent) => {
    event.preventDefault()
    try {
      setError(null)
      await createVacancy(token, vacancyFormData)
      setVacancyFormData({
        title: '',
        position: '',
        language: 'python',
        grade: 'junior',
        ideal_resume: '',
      })
      setShowVacancyForm(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания вакансии')
    }
  }

  const handleUpdateVacancy = async (id: string, data: VacancyUpdate) => {
    try {
      setError(null)
      await updateVacancy(token, id, data)
      setEditingVacancyId(null)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления вакансии')
    }
  }

  const handleDeleteVacancy = async (id: string) => {
    if (!confirm('Вы уверены, что хотите удалить эту вакансию?')) {
      return
    }
    try {
      setError(null)
      await deleteVacancy(token, id)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления вакансии')
    }
  }

  // Tasks handlers
  const handleCreateTask = async (event: FormEvent) => {
    event.preventDefault()
    try {
      setError(null)
      await createTask(token, taskFormData)
      setTaskFormData({
        title: '',
        description: '',
        topic: null,
        difficulty: 'medium',
        open_tests: [],
        hidden_tests: [],
        vacancy_id: null,
      })
      setShowTaskForm(false)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания задачи')
    }
  }

  const handleUpdateTask = async (id: string, data: TaskUpdate) => {
    try {
      setError(null)
      await updateTask(token, id, data)
      setEditingTaskId(null)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления задачи')
    }
  }

  const handleDeleteTask = async (id: string) => {
    if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
      return
    }
    try {
      setError(null)
      await deleteTask(token, id)
      await loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления задачи')
    }
  }

  if (loading) {
    return (
      <div className="admin-panel">
        <div className="admin-loading">Загрузка...</div>
      </div>
    )
  }

  const handleLogout = () => {
    // Удаляем только админский токен, не трогая токен основного сервиса
    window.localStorage.removeItem('vibecode_admin_token')
    window.location.href = '/admin'
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <div>
          <h1>Панель администратора</h1>
          <p className="admin-subtitle">Управление вопросами и вакансиями</p>
        </div>
        <button type="button" className="admin-logout-btn" onClick={handleLogout}>
          Выйти
        </button>
      </div>

      <div className="admin-tabs">
        <button
          type="button"
          className={activeTab === 'questions' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('questions')}
        >
          Вопросы
        </button>
        <button
          type="button"
          className={activeTab === 'vacancies' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('vacancies')}
        >
          Вакансии
        </button>
        <button
          type="button"
          className={activeTab === 'tasks' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('tasks')}
        >
          Задачи
        </button>
      </div>

      {error && (
        <div className="admin-error">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {activeTab === 'questions' && (
        <>
          <div className="admin-actions">
            <button
              type="button"
              className="admin-add-btn"
              onClick={() => {
                setShowQuestionForm(true)
                setQuestionFormData({
                  text: '',
                  order: questions.length,
                  question_type: 'text',
                  options: null,
                  difficulty: 'medium',
                  vacancy_id: null,
                })
              }}
            >
              + Добавить вопрос
            </button>
          </div>

          {showQuestionForm && (
            <div className="admin-form-card">
              <div className="admin-form-header">
                <h3>Новый вопрос</h3>
                <button
                  type="button"
                  className="close-btn"
                  onClick={() => {
                    setShowQuestionForm(false)
                    setQuestionFormData({
                      text: '',
                      order: 0,
                      question_type: 'text',
                      options: null,
                      difficulty: 'medium',
                      vacancy_id: null,
                    })
                  }}
                >
                  ×
                </button>
              </div>
              <form onSubmit={handleCreateQuestion}>
                <label>
                  <span className="label-text">Текст вопроса</span>
                  <textarea
                    value={questionFormData.text}
                    onChange={(e) =>
                      setQuestionFormData({ ...questionFormData, text: e.target.value })
                    }
                    placeholder="Введите текст вопроса..."
                    required
                    rows={4}
                  />
                </label>
                <label>
                  <span className="label-text">Тип вопроса</span>
                  <select
                    value={questionFormData.question_type}
                    onChange={(e) =>
                      setQuestionFormData({
                        ...questionFormData,
                        question_type: e.target.value,
                      })
                    }
                  >
                    <option value="text">Текстовый ответ</option>
                    <option value="choice">Выбор одного варианта</option>
                    <option value="multiple_choice">Выбор нескольких вариантов</option>
                  </select>
                </label>
                {(questionFormData.question_type === 'choice' ||
                  questionFormData.question_type === 'multiple_choice') && (
                  <label>
                    <span className="label-text">
                      Варианты ответов (JSON массив, например: ["Вариант 1", "Вариант 2"])
                    </span>
                    <textarea
                      value={questionFormData.options || ''}
                      onChange={(e) =>
                        setQuestionFormData({ ...questionFormData, options: e.target.value })
                      }
                      placeholder='["Вариант 1", "Вариант 2", "Вариант 3"]'
                      rows={3}
                    />
                  </label>
                )}
                <label>
                  <span className="label-text">Порядок отображения</span>
                  <input
                    type="number"
                    value={questionFormData.order ?? 0}
                    onChange={(e) =>
                      setQuestionFormData({
                        ...questionFormData,
                        order: parseInt(e.target.value, 10) || 0,
                      })
                    }
                    min="0"
                  />
                </label>
                <label>
                  <span className="label-text">Уровень сложности (для задач)</span>
                  <select
                    value={questionFormData.difficulty || 'medium'}
                    onChange={(e) =>
                      setQuestionFormData({
                        ...questionFormData,
                        difficulty: e.target.value,
                      })
                    }
                  >
                    <option value="easy">Легкая</option>
                    <option value="medium">Средняя</option>
                    <option value="hard">Сложная</option>
                  </select>
                </label>
                <label>
                  <span className="label-text">Вакансия (необязательно)</span>
                  <select
                    value={questionFormData.vacancy_id || ''}
                    onChange={(e) =>
                      setQuestionFormData({
                        ...questionFormData,
                        vacancy_id: e.target.value || null,
                      })
                    }
                  >
                    <option value="">Без привязки к вакансии</option>
                    {vacancies.map((vacancy) => (
                      <option key={vacancy.id} value={vacancy.id}>
                        {vacancy.title} ({vacancy.language} - {vacancy.grade})
                      </option>
                    ))}
                  </select>
                </label>
                <div className="admin-form-actions">
                  <button type="submit" className="submit-btn">
                    Создать
                  </button>
                  <button
                    type="button"
                    className="ghost"
                    onClick={() => {
                      setShowQuestionForm(false)
                      setQuestionFormData({
                        text: '',
                        order: 0,
                        question_type: 'text',
                        options: null,
                        difficulty: 'medium',
                        vacancy_id: null,
                      })
                    }}
                  >
                    Отмена
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="questions-list">
            {questions.length === 0 ? (
              <div className="admin-empty">Нет вопросов. Добавьте первый вопрос.</div>
            ) : (
              questions.map((question) => (
                <div key={question.id} className="question-card">
                  {editingQuestionId === question.id ? (
                    <div className="question-edit">
                      <label>
                        <span className="label-text">Текст вопроса</span>
                        <textarea
                          value={questionFormData.text}
                          onChange={(e) =>
                            setQuestionFormData({ ...questionFormData, text: e.target.value })
                          }
                          required
                          rows={3}
                        />
                      </label>
                      <label>
                        <span className="label-text">Тип вопроса</span>
                        <select
                          value={questionFormData.question_type}
                          onChange={(e) =>
                            setQuestionFormData({
                              ...questionFormData,
                              question_type: e.target.value,
                            })
                          }
                        >
                          <option value="text">Текстовый ответ</option>
                          <option value="choice">Выбор одного варианта</option>
                          <option value="multiple_choice">Выбор нескольких вариантов</option>
                        </select>
                      </label>
                      {(questionFormData.question_type === 'choice' ||
                        questionFormData.question_type === 'multiple_choice') && (
                        <label>
                          <span className="label-text">Варианты ответов (JSON)</span>
                          <textarea
                            value={questionFormData.options || ''}
                            onChange={(e) =>
                              setQuestionFormData({
                                ...questionFormData,
                                options: e.target.value,
                              })
                            }
                            rows={3}
                          />
                        </label>
                      )}
                      <label>
                        <span className="label-text">Порядок</span>
                        <input
                          type="number"
                          value={questionFormData.order ?? 0}
                          onChange={(e) =>
                            setQuestionFormData({
                              ...questionFormData,
                              order: parseInt(e.target.value, 10) || 0,
                            })
                          }
                          min="0"
                        />
                      </label>
                      <label>
                        <span className="label-text">Уровень сложности</span>
                        <select
                          value={questionFormData.difficulty || 'medium'}
                          onChange={(e) =>
                            setQuestionFormData({
                              ...questionFormData,
                              difficulty: e.target.value,
                            })
                          }
                        >
                          <option value="easy">Легкая</option>
                          <option value="medium">Средняя</option>
                          <option value="hard">Сложная</option>
                        </select>
                      </label>
                      <label>
                        <span className="label-text">Вакансия (необязательно)</span>
                        <select
                          value={questionFormData.vacancy_id || ''}
                          onChange={(e) =>
                            setQuestionFormData({
                              ...questionFormData,
                              vacancy_id: e.target.value || null,
                            })
                          }
                        >
                          <option value="">Без привязки к вакансии</option>
                          {vacancies.map((vacancy) => (
                            <option key={vacancy.id} value={vacancy.id}>
                              {vacancy.title} ({vacancy.language} - {vacancy.grade})
                            </option>
                          ))}
                        </select>
                      </label>
                      <div className="question-edit-actions">
                        <button
                          type="button"
                          className="submit-btn"
                          onClick={() => handleUpdateQuestion(question.id, questionFormData)}
                        >
                          Сохранить
                        </button>
                        <button
                          type="button"
                          className="ghost"
                          onClick={() => {
                            setEditingQuestionId(null)
                            setQuestionFormData({
                              text: '',
                              order: 0,
                              question_type: 'text',
                              options: null,
                              difficulty: 'medium',
                              vacancy_id: null,
                            })
                          }}
                        >
                          Отмена
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="question-content">
                        <div className="question-order">#{question.order}</div>
                        <div className="question-text">{question.text}</div>
                        <div className="question-meta">
                          Тип: {question.question_type} | Сложность: {question.difficulty || 'medium'}
                          {question.vacancy_id && (
                            <span> | Вакансия: {
                              vacancies.find(v => v.id === question.vacancy_id)?.title || question.vacancy_id
                            }</span>
                          )}
                          {' '}| Создан:{' '}
                          {new Date(question.created_at).toLocaleDateString('ru-RU', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                          })}
                        </div>
                      </div>
                      <div className="question-actions">
                        <button
                          type="button"
                          className="edit-btn"
                          onClick={() => {
                            setEditingQuestionId(question.id)
                            setQuestionFormData({
                              text: question.text,
                              order: question.order,
                              question_type: question.question_type,
                              options: question.options,
                              difficulty: question.difficulty || 'medium',
                              vacancy_id: question.vacancy_id || null,
                            })
                          }}
                        >
                          Редактировать
                        </button>
                        <button
                          type="button"
                          className="delete-btn"
                          onClick={() => handleDeleteQuestion(question.id)}
                        >
                          Удалить
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}

      {activeTab === 'vacancies' && (
        <>
          <div className="admin-actions">
            <button
              type="button"
              className="admin-add-btn"
              onClick={() => {
                setShowVacancyForm(true)
                setVacancyFormData({
                  title: '',
                  position: '',
                  language: 'python',
                  grade: 'junior',
                  ideal_resume: '',
                })
              }}
            >
              + Добавить вакансию
            </button>
          </div>

          {showVacancyForm && (
            <div className="admin-form-card">
              <div className="admin-form-header">
                <h3>Новая вакансия</h3>
                <button
                  type="button"
                  className="close-btn"
                  onClick={() => {
                    setShowVacancyForm(false)
                    setVacancyFormData({
                      title: '',
                      position: '',
                      language: 'python',
                      grade: 'junior',
                      ideal_resume: '',
                    })
                  }}
                >
                  ×
                </button>
              </div>
              <form onSubmit={handleCreateVacancy}>
                <label>
                  <span className="label-text">Название вакансии</span>
                  <input
                    type="text"
                    value={vacancyFormData.title}
                    onChange={(e) =>
                      setVacancyFormData({ ...vacancyFormData, title: e.target.value })
                    }
                    placeholder="Например: Backend Developer"
                    required
                  />
                </label>
                <label>
                  <span className="label-text">Позиция</span>
                  <input
                    type="text"
                    value={vacancyFormData.position}
                    onChange={(e) =>
                      setVacancyFormData({ ...vacancyFormData, position: e.target.value })
                    }
                    placeholder="Например: Backend Developer"
                    required
                  />
                </label>
                <label>
                  <span className="label-text">Язык программирования</span>
                  <select
                    value={vacancyFormData.language}
                    onChange={(e) =>
                      setVacancyFormData({ ...vacancyFormData, language: e.target.value })
                    }
                  >
                    <option value="python">Python</option>
                    <option value="typescript">TypeScript</option>
                    <option value="go">Go</option>
                    <option value="java">Java</option>
                  </select>
                </label>
                <label>
                  <span className="label-text">Грейд</span>
                  <select
                    value={vacancyFormData.grade}
                    onChange={(e) =>
                      setVacancyFormData({ ...vacancyFormData, grade: e.target.value })
                    }
                  >
                    <option value="junior">Junior</option>
                    <option value="middle">Middle</option>
                    <option value="senior">Senior</option>
                  </select>
                </label>
                <label>
                  <span className="label-text">Идеальное резюме</span>
                  <textarea
                    value={vacancyFormData.ideal_resume}
                    onChange={(e) =>
                      setVacancyFormData({ ...vacancyFormData, ideal_resume: e.target.value })
                    }
                    placeholder="Описание идеального резюме для этой вакансии..."
                    required
                    rows={6}
                  />
                </label>
                <div className="admin-form-actions">
                  <button type="submit" className="submit-btn">
                    Создать
                  </button>
                  <button
                    type="button"
                    className="ghost"
                    onClick={() => {
                      setShowVacancyForm(false)
                      setVacancyFormData({
                        title: '',
                        position: '',
                        language: 'python',
                        grade: 'junior',
                        ideal_resume: '',
                      })
                    }}
                  >
                    Отмена
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="questions-list">
            {vacancies.length === 0 ? (
              <div className="admin-empty">Нет вакансий. Добавьте первую вакансию.</div>
            ) : (
              vacancies.map((vacancy) => (
                <div key={vacancy.id} className="question-card">
                  {editingVacancyId === vacancy.id ? (
                    <div className="question-edit">
                      <label>
                        <span className="label-text">Название</span>
                        <input
                          type="text"
                          value={vacancyFormData.title}
                          onChange={(e) =>
                            setVacancyFormData({ ...vacancyFormData, title: e.target.value })
                          }
                          required
                        />
                      </label>
                      <label>
                        <span className="label-text">Позиция</span>
                        <input
                          type="text"
                          value={vacancyFormData.position}
                          onChange={(e) =>
                            setVacancyFormData({ ...vacancyFormData, position: e.target.value })
                          }
                          required
                        />
                      </label>
                      <label>
                        <span className="label-text">Язык</span>
                        <select
                          value={vacancyFormData.language}
                          onChange={(e) =>
                            setVacancyFormData({ ...vacancyFormData, language: e.target.value })
                          }
                        >
                          <option value="python">Python</option>
                          <option value="typescript">TypeScript</option>
                          <option value="go">Go</option>
                          <option value="java">Java</option>
                        </select>
                      </label>
                      <label>
                        <span className="label-text">Грейд</span>
                        <select
                          value={vacancyFormData.grade}
                          onChange={(e) =>
                            setVacancyFormData({ ...vacancyFormData, grade: e.target.value })
                          }
                        >
                          <option value="junior">Junior</option>
                          <option value="middle">Middle</option>
                          <option value="senior">Senior</option>
                        </select>
                      </label>
                      <label>
                        <span className="label-text">Идеальное резюме</span>
                        <textarea
                          value={vacancyFormData.ideal_resume}
                          onChange={(e) =>
                            setVacancyFormData({
                              ...vacancyFormData,
                              ideal_resume: e.target.value,
                            })
                          }
                          required
                          rows={4}
                        />
                      </label>
                      <div className="question-edit-actions">
                        <button
                          type="button"
                          className="submit-btn"
                          onClick={() => handleUpdateVacancy(vacancy.id, vacancyFormData)}
                        >
                          Сохранить
                        </button>
                        <button
                          type="button"
                          className="ghost"
                          onClick={() => {
                            setEditingVacancyId(null)
                            setVacancyFormData({
                              title: '',
                              position: '',
                              language: 'python',
                              grade: 'junior',
                              ideal_resume: '',
                            })
                          }}
                        >
                          Отмена
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="question-content">
                        <div className="question-text">
                          <strong>{vacancy.title}</strong> - {vacancy.position}
                        </div>
                        <div className="question-meta">
                          Язык: {vacancy.language} | Грейд: {vacancy.grade} | Создана:{' '}
                          {new Date(vacancy.created_at).toLocaleDateString('ru-RU', {
                            day: '2-digit',
                            month: '2-digit',
                            year: 'numeric',
                          })}
                        </div>
                        <div className="question-text" style={{ marginTop: '12px' }}>
                          <strong>Идеальное резюме:</strong>
                          <p style={{ marginTop: '8px', opacity: 0.8 }}>
                            {vacancy.ideal_resume}
                          </p>
                        </div>
                      </div>
                      <div className="question-actions">
                        <button
                          type="button"
                          className="edit-btn"
                          onClick={() => {
                            setEditingVacancyId(vacancy.id)
                            setVacancyFormData({
                              title: vacancy.title,
                              position: vacancy.position,
                              language: vacancy.language,
                              grade: vacancy.grade,
                              ideal_resume: vacancy.ideal_resume,
                            })
                          }}
                        >
                          Редактировать
                        </button>
                        <button
                          type="button"
                          className="delete-btn"
                          onClick={() => handleDeleteVacancy(vacancy.id)}
                        >
                          Удалить
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}

      {activeTab === 'tasks' && (
        <>
          <div className="admin-actions">
            <button
              type="button"
              className="admin-add-btn"
              onClick={() => {
                setShowTaskForm(true)
                setTaskFormData({
                  title: '',
                  description: '',
                  topic: null,
                  difficulty: 'medium',
                  open_tests: [],
                  hidden_tests: [],
                  vacancy_id: null,
                })
              }}
            >
              + Добавить задачу
            </button>
          </div>

          {showTaskForm && (
            <div className="admin-form-card">
              <div className="admin-form-header">
                <h3>{editingTaskId ? 'Редактировать задачу' : 'Новая задача'}</h3>
                <button
                  type="button"
                  className="close-btn"
                  onClick={() => {
                    setShowTaskForm(false)
                    setEditingTaskId(null)
                    setTaskFormData({
                      title: '',
                      description: '',
                      topic: null,
                      difficulty: 'medium',
                      open_tests: [],
                      hidden_tests: [],
                      vacancy_id: null,
                    })
                  }}
                >
                  ×
                </button>
              </div>
              <form onSubmit={editingTaskId ? (e) => { e.preventDefault(); handleUpdateTask(editingTaskId, taskFormData) } : handleCreateTask}>
                <label>
                  <span className="label-text">Название задачи</span>
                  <input
                    type="text"
                    value={taskFormData.title}
                    onChange={(e) => setTaskFormData({ ...taskFormData, title: e.target.value })}
                    required
                  />
                </label>
                <label>
                  <span className="label-text">Условие задачи</span>
                  <textarea
                    value={taskFormData.description}
                    onChange={(e) => setTaskFormData({ ...taskFormData, description: e.target.value })}
                    rows={10}
                    required
                  />
                </label>
                <label>
                  <span className="label-text">Тема/категория</span>
                  <input
                    type="text"
                    value={taskFormData.topic || ''}
                    onChange={(e) => setTaskFormData({ ...taskFormData, topic: e.target.value || null })}
                  />
                </label>
                <label>
                  <span className="label-text">Сложность</span>
                  <select
                    value={taskFormData.difficulty}
                    onChange={(e) => setTaskFormData({ ...taskFormData, difficulty: e.target.value as 'easy' | 'medium' | 'hard' })}
                  >
                    <option value="easy">Легкая</option>
                    <option value="medium">Средняя</option>
                    <option value="hard">Сложная</option>
                  </select>
                </label>
                <label>
                  <span className="label-text">Вакансия (опционально)</span>
                  <select
                    value={taskFormData.vacancy_id || ''}
                    onChange={(e) => setTaskFormData({ ...taskFormData, vacancy_id: e.target.value || null })}
                  >
                    <option value="">Не привязана</option>
                    {vacancies.map((v) => (
                      <option key={v.id} value={v.id}>
                        {v.title} ({v.language}, {v.grade})
                      </option>
                    ))}
                  </select>
                </label>
                <div className="form-section">
                  <h4>Открытые тесты (JSON массив)</h4>
                  <textarea
                    value={JSON.stringify(taskFormData.open_tests || [], null, 2)}
                    onChange={(e) => {
                      try {
                        const parsed = JSON.parse(e.target.value)
                        setTaskFormData({ ...taskFormData, open_tests: parsed })
                      } catch {
                        // Invalid JSON, keep as is
                      }
                    }}
                    rows={8}
                    placeholder='[{"input": "1 2", "output": "3"}]'
                  />
                </div>
                <div className="form-section">
                  <h4>Закрытые тесты (JSON массив)</h4>
                  <textarea
                    value={JSON.stringify(taskFormData.hidden_tests || [], null, 2)}
                    onChange={(e) => {
                      try {
                        const parsed = JSON.parse(e.target.value)
                        setTaskFormData({ ...taskFormData, hidden_tests: parsed })
                      } catch {
                        // Invalid JSON, keep as is
                      }
                    }}
                    rows={8}
                    placeholder='[{"input": "10 20", "output": "30"}]'
                  />
                </div>
                <button type="submit" className="admin-submit-btn">
                  {editingTaskId ? 'Сохранить' : 'Создать'}
                </button>
              </form>
            </div>
          )}

          <div className="admin-list">
            {tasks.length === 0 ? (
              <div className="admin-empty">Задач пока нет</div>
            ) : (
              tasks.map((task) => (
                <div key={task.id} className="admin-item">
                  {editingTaskId === task.id ? (
                    <div className="admin-edit-form">
                      <input
                        type="text"
                        value={taskFormData.title}
                        onChange={(e) => setTaskFormData({ ...taskFormData, title: e.target.value })}
                        className="edit-input"
                      />
                      <textarea
                        value={taskFormData.description}
                        onChange={(e) => setTaskFormData({ ...taskFormData, description: e.target.value })}
                        className="edit-textarea"
                        rows={5}
                      />
                      <div className="edit-actions">
                        <button
                          type="button"
                          className="save-btn"
                          onClick={() => handleUpdateTask(task.id, taskFormData)}
                        >
                          Сохранить
                        </button>
                        <button
                          type="button"
                          className="cancel-btn"
                          onClick={() => {
                            setEditingTaskId(null)
                            setTaskFormData({
                              title: '',
                              description: '',
                              topic: null,
                              difficulty: 'medium',
                              open_tests: [],
                              hidden_tests: [],
                              vacancy_id: null,
                            })
                          }}
                        >
                          Отмена
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="admin-item-content">
                        <h3>{task.title}</h3>
                        <p className="admin-item-meta">
                          Сложность: <strong>{task.difficulty}</strong> | Тема:{' '}
                          {task.topic || 'Не указана'}
                        </p>
                        <div className="admin-item-description">
                          {task.description.substring(0, 200)}
                          {task.description.length > 200 ? '...' : ''}
                        </div>
                        {task.open_tests && task.open_tests.length > 0 && (
                          <div className="admin-item-meta">
                            Открытых тестов: {task.open_tests.length}
                          </div>
                        )}
                        {task.hidden_tests && task.hidden_tests.length > 0 && (
                          <div className="admin-item-meta">
                            Закрытых тестов: {task.hidden_tests.length}
                          </div>
                        )}
                      </div>
                      <div className="question-actions">
                        <button
                          type="button"
                          className="edit-btn"
                          onClick={() => {
                            setEditingTaskId(task.id)
                            setTaskFormData({
                              title: task.title,
                              description: task.description,
                              topic: task.topic,
                              difficulty: task.difficulty,
                              open_tests: task.open_tests || [],
                              hidden_tests: task.hidden_tests || [],
                              vacancy_id: task.vacancy_id,
                            })
                            setShowTaskForm(true)
                          }}
                        >
                          Редактировать
                        </button>
                        <button
                          type="button"
                          className="delete-btn"
                          onClick={() => handleDeleteTask(task.id)}
                        >
                          Удалить
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}

import { type FormEvent, useEffect, useState } from 'react'
import {
  createQuestion,
  deleteQuestion,
  fetchQuestions,
  updateQuestion,
} from '../modules/admin/api'
import type { Question, QuestionCreate, QuestionUpdate } from '../modules/admin/types'
import './AdminPanel.css'

interface AdminPanelProps {
  token: string
  onBack: () => void
}

export function AdminPanel({ token, onBack }: AdminPanelProps) {
  const [questions, setQuestions] = useState<Question[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<QuestionCreate>({ text: '', order: 0 })

  useEffect(() => {
    loadQuestions()
  }, [])

  const loadQuestions = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchQuestions(token)
      setQuestions(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки вопросов')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault()
    try {
      setError(null)
      await createQuestion(token, formData)
      setFormData({ text: '', order: 0 })
      setShowForm(false)
      await loadQuestions()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка создания вопроса')
    }
  }

  const handleUpdate = async (id: string, data: QuestionUpdate) => {
    try {
      setError(null)
      await updateQuestion(token, id, data)
      setEditingId(null)
      await loadQuestions()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка обновления вопроса')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Вы уверены, что хотите удалить этот вопрос?')) {
      return
    }
    try {
      setError(null)
      await deleteQuestion(token, id)
      await loadQuestions()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка удаления вопроса')
    }
  }

  const startEdit = (question: Question) => {
    setEditingId(question.id)
    setFormData({ text: question.text, order: question.order })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setFormData({ text: '', order: 0 })
  }

  if (loading) {
    return (
      <div className="admin-panel">
        <div className="admin-loading">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <div>
          <h1>Панель администратора</h1>
          <p className="admin-subtitle">Управление вопросами для резюме</p>
        </div>
        <button type="button" className="admin-back-btn" onClick={onBack}>
          ← Назад
        </button>
      </div>

      {error && (
        <div className="admin-error">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="admin-actions">
        <button
          type="button"
          className="admin-add-btn"
          onClick={() => {
            setShowForm(true)
            setFormData({ text: '', order: questions.length })
          }}
        >
          + Добавить вопрос
        </button>
      </div>

      {showForm && (
        <div className="admin-form-card">
          <div className="admin-form-header">
            <h3>Новый вопрос</h3>
            <button
              type="button"
              className="close-btn"
              onClick={() => {
                setShowForm(false)
                setFormData({ text: '', order: 0 })
              }}
            >
              ×
            </button>
          </div>
          <form onSubmit={handleCreate}>
            <label>
              <span className="label-text">Текст вопроса</span>
              <textarea
                value={formData.text}
                onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                placeholder="Введите текст вопроса..."
                required
                rows={4}
              />
            </label>
            <label>
              <span className="label-text">Порядок отображения</span>
              <input
                type="number"
                value={formData.order ?? 0}
                onChange={(e) =>
                  setFormData({ ...formData, order: parseInt(e.target.value, 10) || 0 })
                }
                min="0"
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
                  setShowForm(false)
                  setFormData({ text: '', order: 0 })
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
              {editingId === question.id ? (
                <div className="question-edit">
                  <label>
                    <span className="label-text">Текст вопроса</span>
                    <textarea
                      value={formData.text}
                      onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                      required
                      rows={3}
                    />
                  </label>
                  <label>
                    <span className="label-text">Порядок</span>
                    <input
                      type="number"
                      value={formData.order ?? 0}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          order: parseInt(e.target.value, 10) || 0,
                        })
                      }
                      min="0"
                    />
                  </label>
                  <div className="question-edit-actions">
                    <button
                      type="button"
                      className="submit-btn"
                      onClick={() => handleUpdate(question.id, formData)}
                    >
                      Сохранить
                    </button>
                    <button type="button" className="ghost" onClick={cancelEdit}>
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
                      Создан:{' '}
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
                      onClick={() => startEdit(question)}
                    >
                      Редактировать
                    </button>
                    <button
                      type="button"
                      className="delete-btn"
                      onClick={() => handleDelete(question.id)}
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
    </div>
  )
}


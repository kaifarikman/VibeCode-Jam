import React, { useState } from 'react'
import type { TestCase } from '../modules/tasks/types'

interface TestCasesEditorProps {
  tests: TestCase[]
  onChange: (tests: TestCase[]) => void
  title: string
  description?: string
}

export function TestCasesEditor({ tests, onChange, title, description }: TestCasesEditorProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

  const addTest = () => {
    onChange([...tests, { input: '', output: '' }])
    setExpandedIndex(tests.length)
  }

  const removeTest = (index: number) => {
    const newTests = tests.filter((_, i) => i !== index)
    onChange(newTests)
    if (expandedIndex === index) {
      setExpandedIndex(null)
    } else if (expandedIndex !== null && expandedIndex > index) {
      setExpandedIndex(expandedIndex - 1)
    }
  }

  const updateTest = (index: number, field: 'input' | 'output', value: string) => {
    const newTests = [...tests]
    newTests[index] = { ...newTests[index], [field]: value }
    onChange(newTests)
  }

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  return (
    <div className="test-cases-editor">
      <div className="test-cases-header">
        <div>
          <h4>{title}</h4>
          {description && <p className="test-cases-description">{description}</p>}
        </div>
        <button type="button" className="add-test-btn" onClick={addTest}>
          + Добавить тест
        </button>
      </div>

      {tests.length === 0 ? (
        <div className="test-cases-empty">
          <p>Тестов пока нет. Нажмите "Добавить тест" чтобы создать первый тест.</p>
        </div>
      ) : (
        <div className="test-cases-list">
          {tests.map((test, index) => (
            <div key={index} className="test-case-card">
              <div className="test-case-header">
                <div className="test-case-number">
                  <span className="test-case-badge">Тест #{index + 1}</span>
                  {test.input.trim() && test.output.trim() && (
                    <span className="test-case-status">✓ Готов</span>
                  )}
                  {(!test.input.trim() || !test.output.trim()) && (
                    <span className="test-case-status warning">⚠ Неполный</span>
                  )}
                </div>
                <div className="test-case-actions">
                  <button
                    type="button"
                    className="expand-btn"
                    onClick={() => toggleExpand(index)}
                    aria-label={expandedIndex === index ? 'Свернуть' : 'Развернуть'}
                  >
                    {expandedIndex === index ? '▼' : '▶'}
                  </button>
                  <button
                    type="button"
                    className="remove-test-btn"
                    onClick={() => removeTest(index)}
                    aria-label="Удалить тест"
                  >
                    🗑️
                  </button>
                </div>
              </div>

              {expandedIndex === index && (
                <div className="test-case-content">
                  <div className="test-case-field">
                    <label>
                      <span className="field-label">Входные данные (Input)</span>
                      <textarea
                        value={test.input}
                        onChange={(e) => updateTest(index, 'input', e.target.value)}
                        placeholder="Введите входные данные для теста..."
                        rows={4}
                        className="test-case-textarea"
                      />
                      <div className="field-hint">
                        Может быть пустым, если задача не требует ввода
                      </div>
                    </label>
                  </div>

                  <div className="test-case-field">
                    <label>
                      <span className="field-label">Ожидаемый результат (Output)</span>
                      <textarea
                        value={test.output}
                        onChange={(e) => updateTest(index, 'output', e.target.value)}
                        placeholder="Введите ожидаемый результат..."
                        rows={4}
                        className="test-case-textarea"
                        required
                      />
                      <div className="field-hint">
                        Обязательное поле. Будет сравниваться с выводом программы
                      </div>
                    </label>
                  </div>
                </div>
              )}

              {expandedIndex !== index && (
                <div className="test-case-preview">
                  <div className="preview-row">
                    <strong>Input:</strong>
                    <code>{test.input || '(пусто)'}</code>
                  </div>
                  <div className="preview-row">
                    <strong>Output:</strong>
                    <code>{test.output || '(не указан)'}</code>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


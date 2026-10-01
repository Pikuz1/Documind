import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { QuestionForm, type QuestionFormProps } from './QuestionForm'

function setup(props: Partial<QuestionFormProps> = {}) {
  const onAsk = vi.fn()
  render(<QuestionForm onAsk={onAsk} loading={false} {...props} />)
  return {
    onAsk,
    input: screen.getByTestId('question-input'),
    button: screen.getByTestId('ask-button'),
    user: userEvent.setup(),
  }
}

describe('QuestionForm', () => {
  it('is disabled until a question is typed', async () => {
    const { input, button, user } = setup()
    expect(button).toBeDisabled()

    await user.type(input, '   ')
    expect(button).toBeDisabled()

    await user.type(input, 'What is the notice period?')
    expect(button).toBeEnabled()
  })

  it('asks the trimmed question on click and keeps the text', async () => {
    const { onAsk, input, button, user } = setup()

    await user.type(input, '  What is the notice period?  ')
    await user.click(button)

    expect(onAsk).toHaveBeenCalledWith('What is the notice period?')
    expect(input).toHaveValue('  What is the notice period?  ')
  })

  it('asks on Enter', async () => {
    const { onAsk, input, user } = setup()

    await user.type(input, 'Wie lange ist die Kündigungsfrist?{Enter}')

    expect(onAsk).toHaveBeenCalledWith('Wie lange ist die Kündigungsfrist?')
  })

  it('adds a new line on Shift+Enter instead of asking', async () => {
    const { onAsk, input, user } = setup()

    await user.type(input, 'line one{Shift>}{Enter}{/Shift}line two')

    expect(onAsk).not.toHaveBeenCalled()
    expect(input).toHaveValue('line one\nline two')
  })

  it('does not ask while an input method is composing', async () => {
    const { onAsk, input, user } = setup()
    await user.type(input, 'question')

    fireEvent.keyDown(input, { key: 'Enter', isComposing: true })

    expect(onAsk).not.toHaveBeenCalled()
  })

  it('ignores other keys', async () => {
    const { onAsk, input } = setup()

    fireEvent.keyDown(input, { key: 'a' })

    expect(onAsk).not.toHaveBeenCalled()
  })

  it('shows progress and does not ask again while loading', async () => {
    const { onAsk, input, button } = setup({ loading: true })

    fireEvent.change(input, { target: { value: 'What is the notice period?' } })
    fireEvent.keyDown(input, { key: 'Enter' })

    expect(button).toHaveTextContent('Asking…')
    expect(button).toBeDisabled()
    expect(onAsk).not.toHaveBeenCalled()
  })

  it('can be disabled entirely', () => {
    const { input, button } = setup({ disabled: true })

    expect(input).toBeDisabled()
    expect(button).toBeDisabled()
  })

  it('counts characters against the 500 limit', async () => {
    const { input, user } = setup()

    await user.type(input, 'Hello')

    expect(input).toHaveAttribute('maxLength', '500')
    expect(screen.getByText(/^5\/500/)).toBeInTheDocument()
  })
})

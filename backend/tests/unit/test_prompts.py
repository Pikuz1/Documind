from app.ai.prompts import NOT_FOUND, RAG_PROMPT


def test_prompt_declares_context_and_question_variables() -> None:
    assert set(RAG_PROMPT.input_variables) == {"context", "question"}


def test_prompt_renders_context_and_question() -> None:
    messages = RAG_PROMPT.invoke({"context": "Notice period: 3 months.", "question": "How long?"})

    rendered = [m.content for m in messages.to_messages()]
    assert any("Notice period: 3 months." in text for text in rendered)
    assert any("How long?" in text for text in rendered)


def test_system_prompt_embeds_not_found_phrase() -> None:
    system_message = RAG_PROMPT.messages[0]
    assert NOT_FOUND in system_message.prompt.template


def test_language_rule_is_repeated_next_to_the_question() -> None:
    # Smaller models answer in the passages' language unless reminded beside the question.
    messages = RAG_PROMPT.invoke({"context": "Kündigungsfrist: 3 Monate", "question": "How long?"})

    human = messages.to_messages()[-1].content
    assert human.index("How long?") < human.index("same language as the question")

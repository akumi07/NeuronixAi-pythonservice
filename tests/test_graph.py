import pytest

from app.graph import run


@pytest.mark.parametrize(
    "question",
    ["What does my uploaded PDF say about pricing?", "Summarise the document."],
)
def test_document_questions_go_to_knowledge(question):
    result = run(question)

    assert result["route"] == "knowledge"
    assert result["answer"].startswith("[knowledge]")


@pytest.mark.parametrize(
    "question", ["Hello, how are you?", "Write a haiku about rain."]
)
def test_other_questions_go_to_general(question):
    result = run(question)

    assert result["route"] == "general"
    assert result["answer"].startswith("[general]")

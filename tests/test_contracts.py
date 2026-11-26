import pytest
from pydantic import ValidationError

from app.contracts import (
    AgentName,
    ChatTurnRequest,
    ChatTurnResponse,
    ErrorResponse,
    RetrieveRequest,
    RetrieveResponse,
)


def valid_turn_json() -> dict:
    """A chat-turn request exactly as Java will send it (camelCase)."""
    return {
        "requestId": "req-1",
        "userId": 7,
        "conversationId": 42,
        "message": "Plan my week",
        "selectedAgent": "planning",
        "documentIds": [1, 2],
        "history": [{"role": "user", "content": "hi"}],
    }


def valid_retrieve_json() -> dict:
    return {"userId": 1, "documentIds": [1], "query": "pricing", "topK": 5}


# ---------- ChatTurnRequest ----------


def test_parses_camel_case_json_from_java():
    req = ChatTurnRequest.model_validate(valid_turn_json())
    assert req.user_id == 7
    assert req.conversation_id == 42
    assert req.selected_agent == AgentName.PLANNING
    assert req.history[0].role == "user"


def test_serialises_back_to_camel_case():
    req = ChatTurnRequest.model_validate(valid_turn_json())
    out = req.model_dump(by_alias=True)
    assert "conversationId" in out
    assert "conversation_id" not in out


def test_selected_agent_is_optional():
    data = valid_turn_json()
    del data["selectedAgent"]
    assert ChatTurnRequest.model_validate(data).selected_agent is None


def test_document_ids_and_history_default_to_empty():
    data = valid_turn_json()
    del data["documentIds"]
    del data["history"]
    req = ChatTurnRequest.model_validate(data)
    assert req.document_ids == []
    assert req.history == []


def test_unknown_agent_is_rejected():
    data = valid_turn_json() | {"selectedAgent": "hacker"}
    with pytest.raises(ValidationError):
        ChatTurnRequest.model_validate(data)


def test_unknown_field_is_rejected():
    data = valid_turn_json() | {"isAdmin": True}
    with pytest.raises(ValidationError):
        ChatTurnRequest.model_validate(data)


def test_empty_message_is_rejected():
    data = valid_turn_json() | {"message": ""}
    with pytest.raises(ValidationError):
        ChatTurnRequest.model_validate(data)


def test_more_than_100_documents_is_rejected():
    data = valid_turn_json() | {"documentIds": list(range(101))}
    with pytest.raises(ValidationError):
        ChatTurnRequest.model_validate(data)


def test_missing_required_field_is_rejected():
    data = valid_turn_json()
    del data["userId"]
    with pytest.raises(ValidationError):
        ChatTurnRequest.model_validate(data)


# ---------- ChatTurnResponse ----------


def test_response_serialises_to_contract_shape():
    resp = ChatTurnResponse(
        answer="Here is your plan",
        agent=AgentName.PLANNING,
        route_reason="user selected",
        thread_id="42",
        status="completed",
    )
    out = resp.model_dump(by_alias=True, mode="json")
    assert out == {
        "answer": "Here is your plan",
        "agent": "planning",
        "routeReason": "user selected",
        "citations": [],
        "threadId": "42",
        "status": "completed",
    }


def test_invalid_status_is_rejected():
    with pytest.raises(ValidationError):
        ChatTurnResponse(
            answer="x",
            agent=AgentName.GENERAL,
            route_reason="r",
            thread_id="1",
            status="done",
        )


# ---------- RetrieveRequest / RetrieveResponse ----------


def test_retrieve_request_defaults_top_k_to_5():
    data = valid_retrieve_json()
    del data["topK"]
    assert RetrieveRequest.model_validate(data).top_k == 5


@pytest.mark.parametrize("top_k", [0, 21])
def test_top_k_must_be_between_1_and_20(top_k):
    with pytest.raises(ValidationError):
        RetrieveRequest.model_validate(valid_retrieve_json() | {"topK": top_k})


def test_retrieve_needs_at_least_one_document():
    with pytest.raises(ValidationError):
        RetrieveRequest.model_validate(valid_retrieve_json() | {"documentIds": []})


def test_retrieve_response_parses_java_json():
    resp = RetrieveResponse.model_validate(
        {
            "chunks": [
                {"chunkId": 9, "documentId": 1, "page": 3, "text": "Price is 10", "score": 0.82}
            ]
        }
    )
    assert resp.chunks[0].page == 3
    assert resp.chunks[0].score == pytest.approx(0.82)


def test_chunk_page_must_be_at_least_1():
    with pytest.raises(ValidationError):
        RetrieveResponse.model_validate(
            {"chunks": [{"chunkId": 9, "documentId": 1, "page": 0, "text": "x", "score": 0.5}]}
        )


# ---------- ErrorResponse ----------


def test_error_response_parses_java_error_with_field_errors():
    err = ErrorResponse.model_validate(
        {
            "timestamp": "2026-11-19T10:16:02Z",
            "status": 400,
            "error": "VALIDATION_FAILED",
            "message": "Request has invalid fields",
            "path": "/internal/v1/rag/retrieve",
            "fieldErrors": {"topK": "must be between 1 and 20"},
        }
    )
    assert err.field_errors == {"topK": "must be between 1 and 20"}
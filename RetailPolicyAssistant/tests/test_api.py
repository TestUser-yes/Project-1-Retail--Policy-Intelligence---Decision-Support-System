from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_home() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Retail Policy Assistant Running"}


def test_ask_returns_rag_policy_answer() -> None:
    response = client.post("/ask", json={"question": "What is the data retention policy?"})

    assert response.status_code == 200
    body = response.json()
    assert "retained for" in body["answer"].lower()
    assert body["route"] == "rag"
    assert body["confidence"] == 0.8
    assert body["escalation_required"] is False


def test_ask_returns_sql_vendor_answer() -> None:
    response = client.post("/ask", json={"question": "What is the status of vendor Acme Supplies?"})

    assert response.status_code == 200
    body = response.json()
    assert "vendor acme supplies" in body["answer"].lower()
    assert body["route"] == "sql"
    assert body["confidence"] == 0.85
    assert body["sources"]


def test_ask_returns_hybrid_answer() -> None:
    response = client.post("/ask", json={"question": "Explain retention policy for vendor Acme Supplies."})

    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "hybrid"
    assert body["confidence"] == 0.85
    assert len(body["answer"]) > 20
    assert body["sources"]


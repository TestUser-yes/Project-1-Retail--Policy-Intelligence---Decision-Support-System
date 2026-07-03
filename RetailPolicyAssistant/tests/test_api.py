from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Retail Policy Assistant Running"}


def test_ask_returns_rag_policy_answer() -> None:
    response = client.post("/ask", json={"query": "What does the policy say about escalations for high-risk cases?"})

    assert response.status_code == 200
    body = response.json()
    assert "escalation" in body["answer"].lower()
    assert body["route"] == "rag"
    assert body["confidence"] >= 0.8
    assert body["escalate"] is False
    assert body["reason"]


def test_ask_returns_sql_vendor_answer() -> None:
    response = client.post("/ask", json={"query": "What is the status of vendor Acme Supplies?"})

    assert response.status_code == 200
    body = response.json()
    assert "acme supplies" in body["answer"].lower()
    assert body["route"] == "sql"
    assert body["confidence"] >= 0.85
    assert body["escalate"] is False
    assert body["reason"]


def test_ask_returns_hybrid_answer() -> None:
    response = client.post("/ask", json={"query": "Explain escalation policy for vendor Acme Supplies."})

    assert response.status_code == 200
    body = response.json()
    assert body["route"] == "hybrid"
    assert body["confidence"] >= 0.9
    assert len(body["answer"]) > 20
    assert "[POLICY CONTEXT]" in body["answer"]
    assert "[STRUCTURED DATA]" in body["answer"]
    assert body["escalate"] is False
    assert body["reason"]

from app.models import PolicyDocument


def test_policy_document_model_exists_with_vector_column():
    assert PolicyDocument.__tablename__ == "policy_documents"
    assert "content" in PolicyDocument.__table__.columns
    assert "embedding" in PolicyDocument.__table__.columns

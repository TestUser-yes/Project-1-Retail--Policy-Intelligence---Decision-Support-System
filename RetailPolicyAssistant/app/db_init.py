from app.models.base import Base
from app.database.session import engine

from app.models.vendors import Vendor
from app.models.compliance import ComplianceReview
from app.models.audit import AuditLog
from app.models.policy import PolicyDocument
from app.models.ai_queries import AIQuery
from app.models.ai_response import AIResponse
from app.models.trace import AgentTrace
from app.models.evaluation import EvaluationRun, EvaluationResult


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


if __name__ == "__main__":
    init_db()
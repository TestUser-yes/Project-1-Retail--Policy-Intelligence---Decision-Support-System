from app.models.base import Base
from app.database.session import engine

# import all models so they register with Base
from app.models.vendors import Vendor
from app.models.compliance import ComplianceReview
from app.models.audit import AuditLog
from app.models.policy import PolicyDocument
from app.models.ai_queries import AIQuery
from app.models.ai_response import AIResponse
from app.models.trace import AgentTrace


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

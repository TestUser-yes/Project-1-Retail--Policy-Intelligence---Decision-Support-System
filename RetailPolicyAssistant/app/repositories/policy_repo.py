from app.models.policy import PolicyDocument


class PolicyRepository:
    def __init__(self, db):
        self.db = db

    def search(self, term: str):
        return (
            self.db.query(PolicyDocument)
            .filter(PolicyDocument.content.ilike(f"%{term}%"))
            .limit(5)
            .all()
        )

    def create(self, title: str, content: str, source: str, embedding=None):
        document = PolicyDocument(
            title=title,
            content=content,
            source=source,
            embedding=embedding,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

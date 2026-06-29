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

    def create(
        self,
        document_name: str,
        page_number: int,
        chunk_number: int,
        content: str,
        section: str | None = None,
        embedding=None,
    ):
        document = PolicyDocument(
            document_name=document_name,
            page_number=page_number,
            chunk_number=chunk_number,
            section=section,
            content=content,
            embedding=embedding,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

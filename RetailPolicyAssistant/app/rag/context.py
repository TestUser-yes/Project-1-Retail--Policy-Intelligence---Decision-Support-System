from app.models import PolicyDocument


def build_context(chunks: list[PolicyDocument]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        text = chunk.content.strip()
        parts.append(
            f"""=========================DOCUMENT {i}=========================
Document : {chunk.document_name}
Page     : {chunk.page_number}
Section  : {chunk.section or "N/A"}
TEXT-----
{text}"""
        )
    return "\n".join(parts)

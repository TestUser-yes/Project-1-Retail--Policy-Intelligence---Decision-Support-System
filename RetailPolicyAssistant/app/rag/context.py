from app.models import PolicyDocument


def build_context(chunks: list[PolicyDocument]) -> str:
    """
    Convert retrieved chunks into a single context block.
    """
    context = []
    for chunk in chunks:
        context.append(
            f"""Document: {chunk.document_name}
Page: {chunk.page_number}
Section: {chunk.section}
{chunk.content}"""
        )
    return "\n\n---------------------------\n\n".join(context)

import re

from langchain_core.documents import Document


MAX_CHUNK_SIZE = 1400


def _split_large_section(document_name, page, section, text):
    """
    Split only very large sections while preserving paragraphs.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current = ""

    for para in paragraphs:

        if len(current) + len(para) < MAX_CHUNK_SIZE:
            current += "\n\n" + para

        else:
            chunks.append(
                Document(
                    page_content=current.strip(),
                    metadata={
                        "document_name": document_name,
                        "page": page,
                        "section": section,
                    },
                )
            )

            current = para

    if current.strip():
        chunks.append(
            Document(
                page_content=current.strip(),
                metadata={
                    "document_name": document_name,
                    "page": page,
                    "section": section,
                },
            )
        )

    return chunks


def split_documents(documents):
    """
    Split documents by policy sections instead of fixed characters.
    Keeps tables with their headings.
    """

    final_chunks = []

    section_regex = re.compile(
        r"(?=\n\d+(?:\.\d+)*\s+[A-Z])"
    )

    for doc in documents:

        text = doc.page_content

        sections = section_regex.split(text)

        if len(sections) <= 1:
            final_chunks.append(doc)
            continue

        for section in sections:
            if not section:
                continue

            section = section.strip()

            if not section:
                continue

            heading = section.split("\n")[0]

            if len(section) <= MAX_CHUNK_SIZE:

                final_chunks.append(
                    Document(
                        page_content=section,
                        metadata={
                            **doc.metadata,
                            "section": heading,
                        },
                    )
                )

            else:

                final_chunks.extend(
                    _split_large_section(
                        doc.metadata["document_name"],
                        doc.metadata["page"],
                        heading,
                        section,
                    )
                )

    return final_chunks
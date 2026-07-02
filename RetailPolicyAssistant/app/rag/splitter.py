from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
)


def split_documents(documents):
    """
    Split PDF pages into overlapping chunks.
    """
    return splitter.split_documents(documents)

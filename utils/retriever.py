import numpy as np
import faiss
from utils.embedder import embed_texts, embed_query


class VectorRetriever:
    """
    Builds a FAISS flat L2 index over text chunks and retrieves
    the most semantically similar ones for a given query.
    """

    def __init__(self) -> None:
        self._index: faiss.IndexFlatL2 | None = None
        self._chunks: list[str] = []

    def add_documents(self, chunks: list[str]) -> None:
        """
        Embed all chunks and load them into the FAISS index.

        Args:
            chunks: List of text strings to index.
        """
        self._chunks = chunks
        embeddings = embed_texts(chunks)
        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatL2(dim)
        self._index.add(embeddings)

    def retrieve_relevant_chunks(self, query: str, top_k: int = 5) -> list[str]:
        """
        Return the top-k chunks most similar to the query.

        Args:
            query: User question string.
            top_k: Number of chunks to return.

        Returns:
            List of relevant chunk strings.
        """
        if self._index is None or not self._chunks:
            return []

        q_vec = embed_query(query).reshape(1, -1)
        k = min(top_k, len(self._chunks))
        _, indices = self._index.search(q_vec, k)
        return [self._chunks[i] for i in indices[0] if i < len(self._chunks)]

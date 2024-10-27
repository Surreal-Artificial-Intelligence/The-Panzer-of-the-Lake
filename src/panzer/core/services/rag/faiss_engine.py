import faiss
import numpy as np
from core.models.responses.vector_search_response import VectorSearchResponse


class FaissEngine:
    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu

    def add_embeddings(self, embeddings: np.ndarray,):
        if embeddings.ndim != 2:
            raise ValueError(f"Embeddings should be a 2D array, but got {embeddings.ndim} dimensions.")

        self.d = embeddings.shape[1]  # Dimensionality of embeddings
        self.index = faiss.IndexFlatL2(self.d)  # L2 distance index

        embeddings = embeddings.astype(np.float32)

        # Check if the index is trained
        if not self.index.is_trained:
            raise ValueError("The FAISS index is not trained.")

        # Add embeddings to index
        self.index.add(embeddings)

    def search(self, xq: np.ndarray, topk: int = 10) -> VectorSearchResponse:
        """
        Searches the FAISS index for the nearest neighbors to the query.

        :param query: A 2D NumPy array of shape (n_queries, embedding_dim) representing the query vectors.
        :param topk: Number of top results to return (default: 10).
        :return: A list of tuples where each tuple contains (index of result, distance).
        """
        if xq.shape[1] != self.d:
            raise ValueError(f"Query vector dimension {xq.shape[1]} does not match index dimension {self.d}.")

        # Perform search
        distances, indices = self.index.search(xq, topk)

        # Return a list of (index, distance) tuples for each query
        return VectorSearchResponse(indices=indices[0], distances=distances[0])

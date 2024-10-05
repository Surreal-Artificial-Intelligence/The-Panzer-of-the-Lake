import faiss
import numpy as np
from typing import List, Tuple


class FaissEngine:
    def __init__(self, embeddings: np.ndarray, use_gpu: bool = False):
        """
        Initializes the FAISS index with the given embeddings.

        :param embeddings: A 2D NumPy array of shape (n_samples, embedding_dim).
        :param use_gpu: Whether to use GPU for FAISS operations (default: False).
        """
        if embeddings.ndim != 2:
            raise ValueError(f"Embeddings should be a 2D array, but got {embeddings.ndim} dimensions.")

        self.d = embeddings.shape[1]  # Dimensionality of embeddings
        self.index = faiss.IndexFlatL2(self.d)  # L2 distance index

        embeddings = embeddings.astype(np.float32)

        # Check if the index is trained
        if not self.index.is_trained:
            raise ValueError("The FAISS index is not trained.")

        # Add embeddings to the index
        self.index.add(embeddings)

    def search(self, query: np.ndarray, topk: int = 10) -> List[Tuple[int, float]]:
        """
        Searches the FAISS index for the nearest neighbors to the query.

        :param query: A 2D NumPy array of shape (n_queries, embedding_dim) representing the query vectors.
        :param topk: Number of top results to return (default: 10).
        :return: A list of tuples where each tuple contains (index of result, distance).
        """
        if query.shape[1] != self.d:
            raise ValueError(f"Query vector dimension {query.shape[1]} does not match index dimension {self.d}.")

        # Perform search
        distances, indices = self.index.search(query, topk)

        # Return a list of (index, distance) tuples for each query
        return [(int(idx), float(dist)) for idx, dist in zip(indices[0], distances[0])]


# Example usage:
# embeddings = np.random.random((100, 128)).astype('float32')  # Example 100 vectors of 128 dimensions
# engine = FaissEngine(embeddings)
# query_vector = np.random.random((1, 128)).astype('float32')

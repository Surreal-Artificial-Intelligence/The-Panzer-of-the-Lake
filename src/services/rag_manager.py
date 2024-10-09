from typing import List
import numpy as np
from services.faiss_engine import FaissEngine
from services.document_engine import DocumentEngine
from interfaces.base_model import BaseModel
from pathlib import Path


class RAGManager:
    def __init__(self, model_client: BaseModel, document_processor: DocumentEngine, faiss_engine: FaissEngine):
        """
        Initializes the RAG Manager.

        :param model_client: Model client capable of generating embeddings.
        :param document_processor: A processor to handle document chunking.
        """
        self.model_client = model_client
        self.document_processor = document_processor
        self.faiss_engine = faiss_engine

    def process_document(self, document: str, batch_size: int = 32) -> None:
        """
        Processes the document by chunking, embedding, and indexing into FAISS.

        :param document: The raw text of the document to process.
        :param batch_size: The size of batches for embedding generation.
        """
        try:
            chunks = self.document_processor.preprocess_document(Path(document))
            self.document_processor.chunks = chunks
            embeddings = self._get_embeddings_in_batches(chunks, batch_size)

            # Add embeddings to FAISS index
            self.faiss_engine.add_embeddings(embeddings)  # Add batch to FAISS index
        except Exception as e:
            raise RuntimeError(f"Error processing document: {e}")

    def _get_embeddings_in_batches(self, chunks: List[str], batch_size: int) -> np.ndarray:
        """
        Converts document chunks into embeddings using the model client in batches.

        :param chunks: List of text chunks.
        :param batch_size: The size of batches for embedding generation.
        :return: A list of 2D NumPy arrays of embeddings.
        """
        try:
            embeddings_batches = []
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i: i + batch_size]
                emb_resp = self.model_client.embedding(batch)
                embeddings_batches.extend(emb_resp.embeddings)

        except Exception as e:
            raise RuntimeError(f"Error generating embeddings: {e}")

        return np.vstack(embeddings_batches)

    def search_similar_chunks(self, query: str, topk: int = 5) -> List[str]:
        """
        Finds similar document chunks based on the query.

        :param query: The input query for the RAG system.
        :param topk: The number of top results to retrieve (default: 5).
        :return: A list of (chunk_text, similarity_score) tuples.
        """
        try:
            query_emb_resp = self.model_client.embedding([query])
            vect_resp = self.faiss_engine.search(query_emb_resp.embeddings, topk=topk)
            # results = [(int(idx), float(dist)) for idx, dist in zip(vect_resp.indices, vect_resp.distances)]
            return [self.document_processor.chunks[idx] for idx in vect_resp.indices]
        except Exception as e:
            raise RuntimeError(f"Error during similarity search: {e}")

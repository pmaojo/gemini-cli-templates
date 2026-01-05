"""Embedding generation using Sentence Transformers"""
from typing import List, Union
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    """Generate embeddings using a pre-trained transformer model"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384, device: str = None):
        self.model_name = model_name
        self.dimension = dimension

        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"Loading embedding model {model_name} on {self.device}...")
        self.model = SentenceTransformer(model_name, device=self.device)

    def encode(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings

    def encode_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        return self.encode([text])[0]

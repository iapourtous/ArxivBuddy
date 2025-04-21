"""
Module contenant un embedder personnalisé pour ArxivBuddy.

Cette classe définit un embedder basé sur SentenceTransformers,
utilisant le modèle multilingual-e5-large pour la création d'embeddings.
"""

from typing import List
from chromadb.api.types import Documents, Embeddings
from chromadb.utils.embedding_functions import EmbeddingFunction
from sentence_transformers import SentenceTransformer

class MultilingualE5Embedder(EmbeddingFunction):
    """
    Embedder personnalisé utilisant le modèle 'intfloat/multilingual-e5-large'.
    """
    def __init__(self):
        # Initialiser le modèle SentenceTransformer
        self.model = SentenceTransformer('intfloat/multilingual-e5-large')

    def __call__(self, input_texts: Documents) -> Embeddings:
        # Retourner une liste vide si aucun texte
        if not input_texts:
            return []
        # Préfixe recommandé pour ce modèle
        processed = [f"passage: {text}" for text in input_texts]
        # Générer les embeddings
        embeddings = self.model.encode(processed, convert_to_tensor=False)
        # Convertir en liste simple
        return embeddings.tolist()
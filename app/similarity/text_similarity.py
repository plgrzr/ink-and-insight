import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from nltk import sent_tokenize, download
from nltk.corpus import stopwords
from functools import lru_cache
from typing import List, Dict, Tuple
import torch.nn.functional as F

# Download required NLTK data once at module level
for resource in ["punkt", "stopwords"]:
    try:
        download(resource)
    except Exception as e:
        print(f"Error downloading {resource}: {str(e)}")


class OptimizedSemanticAnalyzer:
    def __init__(self, batch_size: int = 8):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/paraphrase-MiniLM-L3-v2"
        )
        self.model = AutoModel.from_pretrained(
            "sentence-transformers/paraphrase-MiniLM-L3-v2"
        )
        self.stop_words = set(stopwords.words("english"))
        self.batch_size = batch_size

        # Move model to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode

    @staticmethod
    @lru_cache(maxsize=1024)
    def preprocess_text(text: str) -> List[str]:
        """Cache preprocessed text segments"""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        segments = []
        for para in paragraphs:
            segments.extend(sent_tokenize(para))
        return segments

    def get_embeddings_batched(self, segments: List[str]) -> np.ndarray:
        """Get BERT embeddings for text segments in batches"""
        embeddings = []

        for i in range(0, len(segments), self.batch_size):
            batch = segments[i : i + self.batch_size]

            # Tokenize batch
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=128,  # Limit token length for speed
                return_tensors="pt",
            ).to(self.device)

            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Mean pooling with attention mask
            attention_mask = inputs["attention_mask"]
            token_embeddings = outputs.last_hidden_state

            # Compute mean pooling efficiently
            mask_expanded = (
                attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            )
            sum_embeddings = torch.sum(token_embeddings * mask_expanded, dim=1)
            sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
            batch_embeddings = (sum_embeddings / sum_mask).cpu().numpy()

            embeddings.append(batch_embeddings)

        return np.vstack(embeddings)

    def compute_similarity_matrix(
        self, embeddings1: np.ndarray, embeddings2: np.ndarray
    ) -> np.ndarray:
        """Compute similarity matrix between two sets of embeddings efficiently"""
        # Normalize embeddings
        embeddings1_normalized = embeddings1 / np.linalg.norm(
            embeddings1, axis=1, keepdims=True
        )
        embeddings2_normalized = embeddings2 / np.linalg.norm(
            embeddings2, axis=1, keepdims=True
        )

        # Compute similarity matrix
        return np.dot(embeddings1_normalized, embeddings2_normalized.T)

    def analyze_semantic_consistency(
        self, text1: str, text2: str
    ) -> Tuple[float, Dict]:
        """Analyze semantic consistency between two texts"""
        # Preprocess texts
        segments1 = self.preprocess_text(text1)
        segments2 = self.preprocess_text(text2)

        # Get embeddings for both texts
        embeddings1 = self.get_embeddings_batched(segments1)
        embeddings2 = self.get_embeddings_batched(segments2)

        # Compute similarity matrix
        similarity_matrix = self.compute_similarity_matrix(embeddings1, embeddings2)

        # Overall similarity is mean of maximum similarities
        similarity = np.mean(np.max(similarity_matrix, axis=1))

        # Analyze internal consistency
        consistency_analysis = {
            "doc1": self._analyze_internal_consistency(segments1, embeddings1),
            "doc2": self._analyze_internal_consistency(segments2, embeddings2),
        }

        return similarity, consistency_analysis

    def _analyze_internal_consistency(
        self, segments: List[str], embeddings: np.ndarray
    ) -> List[Dict]:
        """Analyze internal consistency using vectorized operations"""
        if len(segments) <= 1:
            return []

        # Compute similarities between adjacent segments
        similarity_matrix = self.compute_similarity_matrix(
            embeddings[:-1], embeddings[1:]
        )
        similarities = np.diag(similarity_matrix)

        # Find inconsistencies (similarity below threshold)
        threshold = 0.5
        inconsistent_indices = np.where(similarities < threshold)[0]

        inconsistencies = [
            {
                "segment_index": int(i),
                "segment_text": segments[i],
                "next_segment_text": segments[i + 1],
                "similarity_score": float(similarities[i]),
            }
            for i in inconsistent_indices
        ]

        return inconsistencies


def compute_text_similarity(text1: str, text2: str, batch_size: int = 8) -> Dict:
    """Compute semantic similarity between two texts"""
    analyzer = OptimizedSemanticAnalyzer(batch_size=batch_size)
    similarity, consistency_analysis = analyzer.analyze_semantic_consistency(
        text1, text2
    )

    return {
        "similarity_score": float(similarity),
        "consistency_analysis": consistency_analysis,
    }

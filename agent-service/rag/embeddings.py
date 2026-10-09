from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .config import settings


class EmbeddingModel:
    """Lazy-load BGE-M3 để các lệnh test/đọc file không phải tải model."""

    def __init__(
        self,
        model_name: str = settings.embedding_model,
        device: str = settings.device,
        cache_dir: Path = settings.model_cache_dir,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.cache_dir = cache_dir
        self._model = None

    def _load(self):
        if self._model is None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            from sentence_transformers import SentenceTransformer

            print(f"Đang nạp embedding model: {self.model_name}")
            print(f"Thiết bị: {self.device}")
            print(f"Model cache: {self.cache_dir}")
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=str(self.cache_dir),
            )
        return self._model

    def encode_documents(
        self,
        texts: Sequence[str],
        batch_size: int = settings.embedding_batch_size,
        show_progress_bar: bool = True,
    ) -> list[list[float]]:
        vectors = self._load().encode(
            list(texts),
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
        )
        return vectors.tolist()

    def encode_query(self, query: str) -> list[float]:
        vector = self._load().encode(
            [query],
            batch_size=1,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )[0]
        return vector.tolist()

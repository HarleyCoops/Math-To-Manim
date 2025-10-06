"""Utility helpers for integrating with Nomic Atlas.

This module wraps the official `nomic` SDK to provide a typed, ergonomic
interface for embedding concept strings, creating datasets, and performing
vector search or topic exploration. It is the primary API that other agents
should use when interacting with Atlas.

Example usage:

>>> client = AtlasClient(dataset_name="math-to-manim-knowledge-graph")
>>> client.ensure_dataset()
>>> client.upsert_concepts([
...     AtlasConcept(concept="linear algebra", metadata={"domain": "math"})
... ])
>>> related = client.search_similar("quantum mechanics")

The implementation intentionally avoids importing the `nomic` package at
module import time to allow downstream code to continue functioning when the
SDK is not installed. Consumers should call `AtlasClient.check_install()` (or
handle the `ImportError`) before using Atlas-specific features.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence


class NomicNotInstalledError(RuntimeError):
    """Raised when the `nomic` dependency is missing for Atlas operations."""


def _import_nomic():
    """Import helper that raises a friendly error if `nomic` is missing."""

    try:
        from nomic import AtlasDataset, embed  # type: ignore
    except ImportError as exc:  # pragma: no cover - import guard
        raise NomicNotInstalledError(
            "The `nomic` package is required for Atlas integration. "
            "Install it with `pip install nomic` and ensure your "
            "NOMIC_API_KEY environment variable is set."
        ) from exc

    return AtlasDataset, embed


@dataclass
class AtlasConcept:
    """Represents a concept and optional metadata for Atlas storage."""

    concept: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_atlas_payload(self) -> Dict[str, Any]:
        """Return the data payload expected by Atlas for this concept."""

        payload = {"concept": self.concept}
        payload.update(self.metadata)
        return payload


class AtlasClient:
    """High level helper for interacting with a Nomic Atlas dataset."""

    def __init__(
        self,
        dataset_name: str,
        *,
        embedding_model: str = "nomic-embed-text-v1.5",
        task_type: str = "clustering",
    ) -> None:
        self.dataset_name = dataset_name
        self.embedding_model = embedding_model
        self.task_type = task_type
        self._dataset = None

    # ------------------------------------------------------------------
    # Installation / health checks
    # ------------------------------------------------------------------
    @staticmethod
    def check_install() -> None:
        """Ensure the `nomic` dependency is available."""

        _import_nomic()

    # ------------------------------------------------------------------
    # Dataset management
    # ------------------------------------------------------------------
    def ensure_dataset(self) -> Any:
        """Create or load the configured dataset from Atlas."""

        AtlasDataset, _ = _import_nomic()
        if self._dataset is None:
            self._dataset = AtlasDataset(self.dataset_name)
        return self._dataset

    @property
    def dataset(self) -> Any:
        """Return the cached dataset instance (requires `ensure_dataset`)."""

        if self._dataset is None:
            raise RuntimeError(
                "Atlas dataset not initialised. Call `ensure_dataset()` "
                "before performing operations."
            )
        return self._dataset

    # ------------------------------------------------------------------
    # Embedding helpers
    # ------------------------------------------------------------------
    def embed_texts(self, texts: Sequence[str]) -> List[List[float]]:
        """Generate embeddings for the provided texts."""

        _, embed = _import_nomic()
        response = embed.text(
            texts=texts,
            model=self.embedding_model,
            task_type=self.task_type,
        )
        return response["embeddings"]

    def upsert_concepts(self, concepts: Iterable[AtlasConcept]) -> None:
        """Embed and upload one or more concepts to the dataset."""

        concepts_list = list(concepts)
        if not concepts_list:
            return

        embeddings = self.embed_texts([c.concept for c in concepts_list])
        self.ensure_dataset().add_data(
            embeddings=embeddings,
            data=[c.as_atlas_payload() for c in concepts_list],
        )

    # ------------------------------------------------------------------
    # Search / topic helpers
    # ------------------------------------------------------------------
    def search_similar(
        self,
        query: str,
        *,
        k: int = 10,
        fields: Optional[Sequence[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Perform a vector search against the dataset."""

        dataset = self.ensure_dataset()
        return dataset.vector_search(
            query=query,
            k=k,
            fields=list(fields) if fields is not None else None,
        )

    def list_topics(self) -> Dict[str, Any]:
        """Return the hierarchical topics discovered by Atlas."""

        return self.ensure_dataset().topics

    def create_map(
        self,
        *,
        name: Optional[str] = None,
        colorable_fields: Optional[Sequence[str]] = None,
        id_field: Optional[str] = None,
    ) -> Any:
        """Create an interactive Atlas map for the dataset."""

        return self.ensure_dataset().create_index(
            name=name,
            colorable_fields=list(colorable_fields) if colorable_fields else None,
            id_field=id_field,
        )


__all__ = ["AtlasClient", "AtlasConcept", "NomicNotInstalledError"]



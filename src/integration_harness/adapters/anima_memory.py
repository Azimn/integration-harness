from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

ANIMA_REPOSITORY = "huodebing-alt/anima"
ANIMA_REVISION = "ba215ce72bcaedd147d5d08de6e54555a62952c1"


class DonorUnavailableError(RuntimeError):
    """Raised when the pinned Anima donor is not importable."""


@dataclass(frozen=True)
class MemoryView:
    id: int
    kind: str
    text: str
    importance: float
    strength: float
    access_count: int
    score: float


class AnimaMemoryAdapter:
    """Thin wrapper around Anima's unmodified ``MemoryStore``.

    The adapter deliberately does not reimplement Anima's memory equations.
    It provides a neutral interface and converts donor-specific ``Memory``
    objects into immutable views for harness experiments.
    """

    def __init__(self, store: Any):
        self._store = store

    @classmethod
    def open(
        cls,
        db_path: str | Path,
        embed_fn: Callable[[str], list[float]],
        *,
        now_fn: Optional[Callable[[], float]] = None,
    ) -> "AnimaMemoryAdapter":
        try:
            module = import_module("anima.store")
        except ModuleNotFoundError as exc:
            raise DonorUnavailableError(
                "Anima is not importable. Check out the pinned donor revision and "
                "place it on PYTHONPATH before running donor experiments."
            ) from exc

        store_cls = module.MemoryStore
        if now_fn is None:
            store = store_cls(db_path, embed_fn)
        else:
            store = store_cls(db_path, embed_fn, now_fn=now_fn)
        return cls(store)

    def close(self) -> None:
        self._store.close()

    def remember(
        self,
        kind: str,
        text: str,
        *,
        importance: float = 0.3,
        source: str = "",
        links: Optional[list[int]] = None,
        embed: bool = True,
    ) -> int:
        return int(
            self._store.remember(
                kind,
                text,
                importance=importance,
                source=source,
                links=links,
                embed=embed,
            )
        )

    def recall(self, query: str, k: int = 6, **kwargs: Any) -> list[MemoryView]:
        memories = self._store.recall(query, k=k, **kwargs)
        return [
            MemoryView(
                id=int(m.id),
                kind=str(m.kind),
                text=str(m.text),
                importance=float(m.importance),
                strength=float(m.strength),
                access_count=int(m.access_count),
                score=float(m.score),
            )
            for m in memories
        ]

    def decay_and_forget(self, **kwargs: Any) -> dict[str, int]:
        result = self._store.decay_and_forget(**kwargs)
        return {str(key): int(value) for key, value in result.items()}

    def recent(self, kind: Optional[str] = None, limit: int = 20) -> list[MemoryView]:
        memories = self._store.recent(kind=kind, limit=limit)
        return [
            MemoryView(
                id=int(m.id),
                kind=str(m.kind),
                text=str(m.text),
                importance=float(m.importance),
                strength=float(m.strength),
                access_count=int(m.access_count),
                score=float(m.score),
            )
            for m in memories
        ]

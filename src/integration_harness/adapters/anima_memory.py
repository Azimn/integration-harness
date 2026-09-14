from __future__ import annotations

import hashlib
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Optional

ANIMA_REPOSITORY = "huodebing-alt/anima"
ANIMA_REVISION = "ba215ce72bcaedd147d5d08de6e54555a62952c1"
ANIMA_STORE_GIT_BLOB = "c4e12341f50cd6f0c85df9d808545824c268e576"


class DonorUnavailableError(RuntimeError):
    """Raised when the pinned Anima donor is not importable."""


class DonorRevisionMismatchError(RuntimeError):
    """Raised when the imported donor source is not the pinned implementation."""


@dataclass(frozen=True)
class MemoryView:
    id: int
    kind: str
    text: str
    importance: float
    strength: float
    access_count: int
    score: float


def git_blob_sha1(path: str | Path) -> str:
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def verify_anima_store_module(module: Any) -> str:
    source = getattr(module, "__file__", None)
    if not source:
        raise DonorRevisionMismatchError("imported anima.store has no inspectable source file")
    actual = git_blob_sha1(source)
    if actual != ANIMA_STORE_GIT_BLOB:
        raise DonorRevisionMismatchError(
            "anima.store does not match pinned revision "
            f"{ANIMA_REVISION}: expected blob {ANIMA_STORE_GIT_BLOB}, got {actual}"
        )
    return actual


class AnimaMemoryAdapter:
    """Thin wrapper around Anima's unmodified ``MemoryStore``.

    The adapter deliberately does not reimplement Anima's memory equations.
    It verifies the donor source bytes, then provides a neutral interface and
    converts donor-specific ``Memory`` objects into immutable harness views.
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

        verify_anima_store_module(module)
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

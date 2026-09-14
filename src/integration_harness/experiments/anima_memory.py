from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

from integration_harness.adapters.anima_memory import AnimaMemoryAdapter


VOCAB = ("shared", "orchard", "river")


def deterministic_embed(text: str) -> list[float]:
    words = text.lower().replace(",", " ").replace(".", " ").split()
    vec = [float(sum(1 for word in words if token in word)) for token in VOCAB]
    return vec if any(vec) else [0.001] * len(VOCAB)


@dataclass
class Clock:
    now: float = 1_000_000.0

    def __call__(self) -> float:
        return self.now

    def advance_days(self, days: float) -> None:
        self.now += days * 86_400.0


def _seed(adapter: AnimaMemoryAdapter) -> None:
    adapter.remember(
        "episodic",
        "shared orchard promise",
        importance=0.3,
        source="fixture",
    )
    adapter.remember(
        "episodic",
        "shared river promise",
        importance=0.3,
        source="fixture",
    )


def _run_history(db_path: Path, rehearsal_query: str | None) -> dict:
    clock = Clock()
    adapter = AnimaMemoryAdapter.open(db_path, deterministic_embed, now_fn=clock)
    try:
        _seed(adapter)

        for _ in range(5):
            clock.advance_days(1)
            if rehearsal_query is not None:
                adapter.recall(rehearsal_query, k=1)

        clock.advance_days(55)
        decay = adapter.decay_and_forget()
        final = adapter.recall("shared", k=2, reinforce=0.0)

        return {
            "top": final[0].text if final else None,
            "live": [memory.text for memory in final],
            "decay": decay,
        }
    finally:
        adapter.close()


def run_experiment() -> dict:
    """Run a matched-history test against the unmodified Anima MemoryStore.

    All three conditions start with the same memories and receive the same final
    cue. The only manipulated variable is which memory, if any, was repeatedly
    retrieved during the prior history. The claim is intentionally narrow:
    retrieval history can alter durable memory availability after later decay.
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        history_a = _run_history(root / "history_a.sqlite3", "orchard")
        history_b = _run_history(root / "history_b.sqlite3", "river")
        control = _run_history(root / "control.sqlite3", None)

    passed = (
        history_a["top"] == "shared orchard promise"
        and history_b["top"] == "shared river promise"
        and control["top"] is None
        and history_a["decay"]["archived"] == 1
        and history_b["decay"]["archived"] == 1
        and control["decay"]["archived"] == 2
    )

    return {
        "experiment": "anima-memory-v0.1",
        "claim": "retrieval history changes durable memory availability after forgetting",
        "history_a": history_a,
        "history_b": history_b,
        "control": control,
        "passed": passed,
        "interpretation_limit": (
            "This is a memory-mechanism result. It does not establish improved "
            "character believability or downstream behavioral realism."
        ),
    }


def main() -> int:
    result = run_experiment()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

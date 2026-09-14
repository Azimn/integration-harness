from __future__ import annotations

import importlib.util
import tempfile
import types
import unittest
from pathlib import Path


try:
    ANIMA_AVAILABLE = importlib.util.find_spec("anima.store") is not None
except ModuleNotFoundError:
    ANIMA_AVAILABLE = False


class AnimaProvenanceTests(unittest.TestCase):
    def test_wrong_store_source_is_rejected(self) -> None:
        from integration_harness.adapters.anima_memory import (
            DonorRevisionMismatchError,
            verify_anima_store_module,
        )

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as temp:
            temp.write("class MemoryStore: pass\n")
            path = Path(temp.name)
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        fake_module = types.SimpleNamespace(__file__=str(path))
        with self.assertRaises(DonorRevisionMismatchError):
            verify_anima_store_module(fake_module)


@unittest.skipUnless(ANIMA_AVAILABLE, "pinned Anima donor is not on PYTHONPATH")
class AnimaMemoryExperimentTests(unittest.TestCase):
    def test_pinned_store_source_is_verified(self) -> None:
        import anima.store
        from integration_harness.adapters.anima_memory import (
            ANIMA_STORE_GIT_BLOB,
            verify_anima_store_module,
        )

        self.assertEqual(verify_anima_store_module(anima.store), ANIMA_STORE_GIT_BLOB)

    def test_matched_histories_change_durable_memory_availability(self) -> None:
        from integration_harness.experiments.anima_memory import run_experiment

        result = run_experiment()
        self.assertTrue(result["passed"], result)
        self.assertEqual(result["history_a"]["top"], "shared orchard promise")
        self.assertEqual(result["history_b"]["top"], "shared river promise")
        self.assertIsNone(result["control"]["top"])
        self.assertEqual(result["history_a"]["decay"]["archived"], 1)
        self.assertEqual(result["history_b"]["decay"]["archived"], 1)
        self.assertEqual(result["control"]["decay"]["archived"], 2)

    def test_present_conditions_are_matched(self) -> None:
        from integration_harness.experiments.anima_memory import run_experiment

        result = run_experiment()
        self.assertEqual(result["history_a"]["decay"]["purged"], 0)
        self.assertEqual(result["history_b"]["decay"]["purged"], 0)
        self.assertEqual(
            result["claim"],
            "retrieval history changes durable memory availability after forgetting",
        )
        self.assertIn("does not establish", result["interpretation_limit"])


if __name__ == "__main__":
    unittest.main()

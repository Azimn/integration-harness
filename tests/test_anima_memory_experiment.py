from __future__ import annotations

import importlib.util
import unittest


try:
    ANIMA_AVAILABLE = importlib.util.find_spec("anima.store") is not None
except ModuleNotFoundError:
    ANIMA_AVAILABLE = False


@unittest.skipUnless(ANIMA_AVAILABLE, "pinned Anima donor is not on PYTHONPATH")
class AnimaMemoryExperimentTests(unittest.TestCase):
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

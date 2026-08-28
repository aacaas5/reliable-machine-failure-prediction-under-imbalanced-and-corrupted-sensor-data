from pathlib import Path
import importlib.util
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = PROJECT_ROOT / "publication" / "scripts" / "run_publication_analysis.py"


def load_module():
    spec = importlib.util.spec_from_file_location("publication_analysis", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicationSafeguardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_original_feature_contract(self):
        self.assertEqual(self.module.FEATURE_COLUMNS, [
            "Type", "Air temperature", "Process temperature",
            "Rotational speed", "Torque", "Tool wear",
        ])
        self.assertNotIn(self.module.TARGET_COLUMN, self.module.FEATURE_COLUMNS)
        self.assertTrue(
            set(self.module.FAILURE_MODE_COLUMNS).isdisjoint(self.module.FEATURE_COLUMNS)
        )

    def test_every_output_is_below_publication(self):
        for relative in [
            "results/example.csv", "figures/example.pdf", "tables/example.tex"
        ]:
            path = self.module.output_path(relative)
            path.relative_to(PROJECT_ROOT / "publication")

    def test_parent_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            self.module.output_path("../results/forbidden.csv")

    def test_original_directories_are_not_output_targets(self):
        text = SCRIPT.read_text(encoding="utf-8")
        for forbidden in ["notebooks/", "reports/", "../results", "../figures"]:
            self.assertNotIn(forbidden, text)

    def test_wilson_interval_contains_observed_recall(self):
        low, high = self.module.wilson_interval(42, 51)
        self.assertLess(low, 42 / 51)
        self.assertGreater(high, 42 / 51)

    def test_missing_mask_is_reproducible_and_close_to_requested_fraction(self):
        import numpy as np
        first = np.random.default_rng(42).random((1500, 5)) < 0.30
        second = np.random.default_rng(42).random((1500, 5)) < 0.30
        self.assertTrue(np.array_equal(first, second))
        self.assertLess(abs(first.mean() - 0.30), 0.02)


if __name__ == "__main__":
    unittest.main()

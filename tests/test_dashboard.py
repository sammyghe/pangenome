"""The explorer must never show a number the genome cannot account for.

This is the repository's core discipline applied to its own dashboard. The
first version of the explorer shipped with hand-written figures that looked
exactly like measurements — the failure mode RESULTS.md §0 and CONSTITUTION §8
exist to prevent. These tests keep the page honest.
"""

import json
import tempfile
import unittest
from pathlib import Path

from pangenome.dashboard import export
from pangenome.store import Store


class TestDashboardExport(unittest.TestCase):
    def setUp(self):
        self.store = Store(":memory:")
        self.tmp = Path(tempfile.mkdtemp()) / "data.json"

    def test_export_reports_real_counts(self):
        for i in range(7):
            self.store.observe("src", f"locus-{i}", f"n{i}", "1", float(i), {})
        self.store.commit()
        d = export(self.store, None, self.tmp)
        self.assertEqual(d["live"]["observations"], 7)
        self.assertTrue(self.tmp.exists())

    def test_export_is_valid_json_on_disk(self):
        export(self.store, None, self.tmp)
        loaded = json.loads(self.tmp.read_text(encoding="utf-8"))
        self.assertIn("live", loaded)
        self.assertIn("provenance", loaded)

    def test_empty_organism_reports_zeros_not_placeholders(self):
        """A fresh clone must report nothing, not inherited-looking numbers."""
        d = export(self.store, None, self.tmp)
        self.assertEqual(d["live"]["observations"], 0)
        self.assertEqual(d["live"]["scaffold"], 0)
        self.assertEqual(d["outbreaks"], [])
        self.assertEqual(d["noticed_unprompted"], [])

    def test_provenance_is_stamped(self):
        d = export(self.store, None, self.tmp)
        self.assertIn("LIVE", d["provenance"])
        self.assertIsNotNone(d["generated_at_utc"])

    def test_study_figures_carry_their_own_provenance(self):
        """The measured study numbers are allowed on the page, but only with a
        pointer to how they were produced."""
        d = export(self.store, None, self.tmp)
        self.assertIn("MEASURED", d["study"]["provenance"])
        self.assertIn("pangenome study", d["study"]["provenance"])

    def test_export_never_raises_on_a_damaged_store(self):
        """The dashboard is a read-out, not an organ — it must not cost a beat."""
        self.store.db.execute("DROP TABLE attention_log")
        self.store.commit()
        d = export(self.store, None, self.tmp)
        self.assertEqual(d["live"]["attention_log"], 0)


class TestExplorerHonesty(unittest.TestCase):
    """Static checks on the shipped page itself."""

    ROOT = Path(__file__).resolve().parent.parent / "explorer"

    def test_page_fetches_real_data(self):
        app = (self.ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("data.json", app)
        self.assertIn("hydrateFromGenome", app)

    def test_page_has_a_provenance_banner(self):
        html = (self.ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="data-provenance"', html)

    def test_fixture_panels_are_labelled(self):
        html = (self.ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("src-fixture", html)
        self.assertIn("FIXTURE", html)


if __name__ == "__main__":
    unittest.main()

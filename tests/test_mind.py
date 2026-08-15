"""The brain's claims, as assertions.

The headline claim — same world, different knowledge, different noticing — is
the one that decides whether developmental attention is a mechanism or a story.
It is `TestSalienceExperiment`.
"""

import json
import time
import unittest

from pangenome import control
from pangenome.experiment import run as run_experiment
from pangenome.salience import (AttentionField, INVESTIGATE, INTERRUPT, IGNORE,
                                REMEMBER, concepts_of)
from pangenome.scaffold import Scaffold
from pangenome.store import Store


def field_with(interests: dict, history: list = ()) -> tuple[Store, AttentionField]:
    s = Store(":memory:")
    f = AttentionField(s)
    for c, w in interests.items():
        f.prime(c, w, why="test")
    sc = Scaffold(s, f)
    for text, value in history:
        sc.remember(f.category_of(sorted(text.split())), sorted(text.split()),
                    {"value": value})
    s.commit()
    return s, f


class TestSalienceExperiment(unittest.TestCase):
    """The core hypothesis. If this fails, the attention organ is unjustified."""

    @classmethod
    def setUpClass(cls):
        cls.r = run_experiment(quiet=True)

    def test_attention_does_not_degrade_the_actual_task(self):
        answers = [r["task_answer"] for r in self.r.values()]
        self.assertTrue(all(a == answers[0] for a in answers))
        self.assertEqual(len(answers[0]), 3)

    def test_knowledge_free_organism_notices_nothing(self):
        self.assertEqual(self.r["GENERALIST"]["noticed_count"], 0)

    def test_owners_notice_their_own_domain(self):
        opt = {i for i, _, _ in self.r["OPTICIAN"]["noticed"]}
        tai = {i for i, _, _ in self.r["TAILOR"]["noticed"]}
        self.assertTrue(any("sunglasses" in i or "lens" in i or "glasses" in i
                            for i in opt), opt)
        self.assertTrue(any(k in i for i in tai
                            for k in ("shirt", "trousers", "wool", "silk", "cotton")), tai)

    def test_they_do_not_overlap(self):
        opt = {i for i, _, _ in self.r["OPTICIAN"]["noticed"]}
        tai = {i for i, _, _ in self.r["TAILOR"]["noticed"]}
        self.assertEqual(opt & tai, set())

    def test_the_underpriced_item_is_found_by_surprise_not_novelty(self):
        """The discriminating case: to an optician, sunglasses are the LEAST
        novel thing on the page. Only the surprise channel can find this."""
        top = self.r["OPTICIAN"]["noticed"][0]
        self.assertIn("clearance", top[0])
        self.assertGreater(top[2], 0.3, "should be driven by surprise")


class TestAttention(unittest.TestCase):
    def test_priming_changes_what_is_salient(self):
        _, a = field_with({"sunglasses": 1.0})
        _, b = field_with({"fabric": 1.0})
        item = [("x", "designer sunglasses polarised lens", "m:x", None),
                ("y", "cotton fabric shirt tailored", "m:y", None)]
        sa = {r["subject"]: r["score"] for r in a.scan(item, log=False)}
        sb = {r["subject"]: r["score"] for r in b.scan(item, log=False)}
        self.assertGreater(sa["x"], sa["y"])
        self.assertGreater(sb["y"], sb["x"])

    def test_activation_spreads_to_undeclared_concepts(self):
        """An organism primed only on 'sunglasses' should light up on
        'polarised', because they co-occurred in its past. Nobody declared it."""
        s, f = field_with({"sunglasses": 1.0})
        for _ in range(5):
            f.learn(["sunglasses", "polarised", "lens"])
        s.commit()
        field = f.activation()
        self.assertGreater(field.get("polarised", 0.0), 0.0)

    def test_flat_scene_produces_no_interruption(self):
        """Everything mildly relevant must not mean everything is urgent —
        the failure mode a fixed threshold cannot avoid."""
        _, f = field_with({"lens": 1.0})
        items = [(f"i{n}", "lens lens lens", "m:lens", None) for n in range(10)]
        self.assertTrue(all(r["verdict"] != INTERRUPT for r in f.scan(items, log=False)))

    def test_the_same_item_is_judged_by_its_company(self):
        """The pure relative-competition claim, independent of calibration:
        one identical item, two scenes. Surrounded by things just like it, it is
        unremarkable. Surrounded by irrelevance, it is worth a look."""
        s, f = field_with({"lens": 1.0})
        for _ in range(5):
            f.learn(["lens", "polarised", "eyewear", "frame"])
        s.commit()
        target = ("target", "polarised lens eyewear frame", "m:lens", None)

        crowd = [(f"peer{n}", "polarised lens eyewear frame", "m:lens", None)
                 for n in range(9)] + [target]
        alone = [(f"dull{n}", "soap towel mug detergent", "m:x", None)
                 for n in range(9)] + [target]

        in_crowd = {r["subject"]: r for r in f.scan(crowd, log=False)}["target"]
        stands_out = {r["subject"]: r for r in f.scan(alone, log=False)}["target"]

        self.assertAlmostEqual(in_crowd["score"], stands_out["score"], places=3,
                               msg="raw score must be identical; only context differs")
        self.assertGreater(stands_out["pop"], in_crowd["pop"])
        self.assertEqual(in_crowd["verdict"], IGNORE)
        self.assertNotEqual(stands_out["verdict"], IGNORE)

    def test_surprise_needs_the_right_reference_class(self):
        s, f = field_with({"sunglasses": 1.0},
                          history=[("sunglasses lens", v) for v in
                                   (30, 34, 38, 42, 46, 50)])
        cheap = f.appraise("x", "sunglasses lens", signature="market:sunglasses",
                           value=8.0)
        normal = f.appraise("y", "sunglasses lens", signature="market:sunglasses",
                            value=40.0)
        self.assertGreater(cheap["surprise"], normal["surprise"])

    def test_reinforcement_moves_the_filter(self):
        s, f = field_with({"lens": 1.0})
        f.learn(["lens", "coating"])
        s.commit()
        before = s.q("SELECT base FROM concepts WHERE name='coating'")[0]["base"]
        f.reinforce(["coating"], useful=True)
        after = s.q("SELECT base FROM concepts WHERE name='coating'")[0]["base"]
        self.assertGreater(after, before)

    def test_concepts_ignore_stopwords(self):
        self.assertNotIn("the", concepts_of("the lens and the frame"))
        self.assertIn("lens", concepts_of("the lens and the frame"))


class TestScaffold(unittest.TestCase):
    def setUp(self):
        self.s = Store(":memory:")
        self.sc = Scaffold(self.s, AttentionField(self.s))

    def _over_days(self, signature: str, concepts: list, days: int = 4) -> None:
        """Recurrence means distinct days, not repetition inside one moment.
        Every test that wants a promotion has to earn it the same way."""
        for d in range(days):
            eid = self.sc.remember(signature, concepts, {"v": 1})
            self.s.db.execute("UPDATE episodes SET at=? WHERE id=?",
                              (time.time() - d * 86400, eid))
        self.s.commit()

    def test_one_busy_moment_is_not_recurrence(self):
        """The bug this rule exists to prevent: 300 observations in one beat
        are one scene, and must not manufacture a pattern."""
        for _ in range(300):
            self.sc.remember("burst", ["a", "b"], {"v": 1})
        self.s.commit()
        self.assertEqual(self.sc.consolidate()["patterns"], 0)

    def test_episodes_promote_to_patterns(self):
        self._over_days("late-delivery", ["supplier-x", "delivery"])
        self.assertGreaterEqual(self.sc.consolidate()["patterns"], 1)
        self.assertGreaterEqual(self.sc.summary()["patterns"], 1)

    def test_patterns_generalise_into_abstractions(self):
        self._over_days("late-delivery-x", ["supplier", "delivery", "xco"])
        self._over_days("late-delivery-y", ["supplier", "delivery", "yco"])
        out = self.sc.consolidate()
        self.assertGreaterEqual(out["abstractions"], 1)

    def test_abstraction_ignores_concepts_present_everywhere(self):
        """A concept in every pattern generalises nothing — it is this
        organism's stopword, and promoting it is enumeration, not learning."""
        for n in range(6):
            self._over_days(f"sig-{n}", ["ubiquitous", f"unique-{n}"])
        self.sc.consolidate()
        rows = self.s.q("SELECT signature FROM scaffold WHERE tier='abstraction'")
        self.assertNotIn("ubiquitous", {r["signature"] for r in rows})

    def test_raw_experience_dies_but_only_after_being_consumed(self):
        self._over_days("thing", ["a", "b"])
        self.sc.consolidate()
        live_before = self.s.q("SELECT COUNT(*) n FROM episodes")[0]["n"]
        self.assertGreater(live_before, 0)
        # fast-forward a year; the structure stays, the episodes go
        self.s.db.execute("UPDATE episodes SET at = at - ?", (400 * 86400,))
        out = self.sc.consolidate()
        self.assertGreater(out["forgotten"], 0)
        self.assertGreaterEqual(self.sc.summary()["patterns"], 1)

    def test_unconsumed_episodes_are_never_forgotten(self):
        self.sc.remember("one-off", ["z"], {"v": 1})
        self.s.db.execute("UPDATE episodes SET at = at - ?", (400 * 86400,))
        self.s.commit()
        self.sc.consolidate()
        self.assertEqual(self.s.q("SELECT COUNT(*) n FROM episodes")[0]["n"], 1)

    def test_retention_curve_rewards_rehearsal(self):
        weak = Scaffold.retention(10.0, 1.0, 0)
        rehearsed = Scaffold.retention(10.0, 1.0, 5)
        self.assertGreater(rehearsed, weak)

    def test_sleep_finds_indirect_links_nobody_observed(self):
        """Swanson ABC: A-B and B-C both seen, A-C never. That candidate link
        is the only thing here nobody put in."""
        f = AttentionField(self.s)
        for _ in range(6):
            f.learn(["fish-oil", "blood-viscosity"])
            f.learn(["blood-viscosity", "raynaud"])
        self.s.commit()
        hyps = self.sc.associate()
        pairs = {tuple(sorted((h["a"], h["c"]))) for h in hyps}
        self.assertIn(("fish-oil", "raynaud"), pairs)

    def test_learning_ratio_is_reported(self):
        self._over_days("s", ["a"])
        self.sc.consolidate()
        self.assertIsInstance(self.sc.learning_ratio()["ratio"], float)


class TestControlPlane(unittest.TestCase):
    """Constitution: the owner's stop is not a request the organism evaluates."""

    def setUp(self):
        self.orig = control.CONTROL
        control.CONTROL = control.GENOME_DIR / "CONTROL.test"

    def tearDown(self):
        if control.CONTROL.exists():
            control.CONTROL.unlink()
        control.CONTROL = self.orig

    def test_default_is_run(self):
        self.assertEqual(control.state(), control.RUN)

    def test_freeze_halts_before_anything_runs(self):
        control.set_state(control.FREEZE, "test")
        with self.assertRaises(control.Halted):
            control.assert_permitted()

    def test_kill_halts(self):
        control.set_state(control.KILL, "test")
        with self.assertRaises(control.Halted):
            control.assert_permitted()

    def test_sleep_permits_dreaming_but_not_acting(self):
        control.set_state(control.SLEEP, "test")
        control.assert_permitted()          # does not raise
        self.assertTrue(control.permits("consolidate"))
        self.assertFalse(control.permits("sense"))
        self.assertFalse(control.permits("acquire"))
        self.assertFalse(control.permits("express"))

    def test_corrupt_control_file_fails_closed(self):
        control.CONTROL.write_text("{ not json")
        self.assertEqual(control.state(), control.FREEZE)

    def test_unknown_state_fails_closed(self):
        control.CONTROL.write_text(json.dumps({"state": "MAYBE"}))
        self.assertEqual(control.state(), control.FREEZE)

    def test_only_the_cli_can_write_the_control_file(self):
        """If the organism could write RUN, every guarantee here is theatre."""
        import pathlib
        import re
        pkg = pathlib.Path(control.__file__).parent
        # Precise: `Store.set_state` is an unrelated method of the same name, so
        # match the qualified call and the direct import, not the bare word.
        writers = re.compile(
            r"control\.set_state|from\s+\.control\s+import[^\n]*set_state"
            r"|control\.CONTROL\s*\.\s*write|CONTROL\.write_text")
        offenders = [py.name for py in pkg.rglob("*.py")
                     if py.name not in ("control.py", "cli.py")
                     and writers.search(py.read_text(encoding="utf-8"))]
        self.assertEqual(offenders, [],
                         f"control file written outside the CLI: {offenders}")


class TestPartner(unittest.TestCase):
    """The brain socket, minus any network. talk() itself is not tested here
    because it writes to the real genome and calls a live endpoint — the parts
    that can be wrong offline are the briefing and the suggestion filter."""

    def test_briefing_on_a_young_organism_says_so(self):
        from pangenome.partner import briefing
        s = Store(":memory:")
        f = AttentionField(s)
        b = briefing(s, f, Scaffold(s, f), "hello")
        self.assertIn("little state", b)

    def test_briefing_includes_interests_and_noticed(self):
        from pangenome.partner import briefing
        s = Store(":memory:")
        f = AttentionField(s)
        f.prime("water", 1.0, "business")
        s.db.execute("INSERT INTO attention_log(at,subject,score,verdict,reason)"
                     " VALUES (?,?,?,?,?)",
                     (time.time(), "some/repo", 0.8, "investigate", "test"))
        s.commit()
        b = briefing(s, f, Scaffold(s, f), "anything")
        self.assertIn("water", b)
        self.assertIn("some/repo", b)

    def test_suggestions_require_grounding_in_the_wild(self):
        """'could' and 'help' recur in every conversation; only concepts the
        organism has also seen in the observation stream may be suggested."""
        from pangenome.partner import _suggest_interests
        import json as j
        s = Store(":memory:")
        f = AttentionField(s)
        for _ in range(4):
            s.db.execute(
                "INSERT INTO episodes(at,signature,concepts,detail) VALUES (?,?,?,?)",
                (time.time(), "owner:conversation",
                 j.dumps(["kampala", "could"]), "{}"))
        for _ in range(3):
            f.learn(["kampala", "water"])       # kampala exists in the wild
        s.commit()
        got = _suggest_interests(s)
        self.assertIn("kampala", got)
        self.assertNotIn("could", got)

    def test_fallback_chain_is_ordered_and_deduplicated_intent(self):
        from pangenome.partner import BrainSocket, FALLBACK_CHAIN
        sock = BrainSocket("my-model")
        self.assertEqual(sock.chain[0], "my-model")
        self.assertEqual(sock.chain[1:], FALLBACK_CHAIN)


if __name__ == "__main__":
    unittest.main()

"""tools/check.py: what it accepts, what it rejects, and what it only warns about. Run: python -m unittest"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check  # noqa: E402

# お天気 in JMdict: two senses
JMDICT = {"1002470": {"word": "お天気【おてんき】", "senses": [["weather"], ["mood", "temper"]]}}


def entry(**changes):
    e = {"word": "お天気【おてんき】",
         "senses": [{"eng": ["weather"], "spa": ["tiempo (atmosférico)"]},
                    {"eng": ["mood", "temper"], "spa": ["humor", "estado de ánimo"]}],
         "status": "pending", "source": "player", "refs": [], "comment": ""}
    e.update(changes)
    return e


def run(entries, jmdict=None, layout=True, name="spa.json"):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        data = {"format": 1, "entries": entries}
        path.write_text(check.dump(data) if layout else json.dumps(data), encoding="utf-8")
        report = check.Report()
        found = check.check_file(report, path)
        if jmdict is not None:
            check.check_against_jmdict(report, path.name, found, jmdict, path.stem.endswith("_machine"))
        return report


class CheckTest(unittest.TestCase):
    def test_a_good_entry_passes(self):
        report = run({"1002470": entry()}, JMDICT)
        self.assertEqual((report.errors, report.warnings), ([], []))

    def test_typed_glosses(self):
        senses = [{"eng": ["weather"], "spa": [{"type": "expl", "text": "estado del tiempo"}]},
                  {"eng": ["mood", "temper"], "spa": ["humor", {"type": "lit", "text": "aire del cielo"}]}]
        self.assertEqual(run({"1002470": entry(senses=senses)}).errors, [])

    def test_errors(self):
        cases = {
            "rejected without a reason": entry(status="rejected"),
            "unknown status": entry(status="done"),
            "unknown field": entry(note="x"),
            "a semicolon in a gloss": entry(senses=[{"eng": ["weather"], "spa": ["tiempo; clima"]}]),
            "a literal gloss not last": entry(senses=[{"eng": ["weather"], "spa": [
                {"type": "lit", "text": "aire del cielo"}, "tiempo"]}]),
            "an unknown gloss type": entry(senses=[{"eng": ["weather"], "spa": [{"type": "x", "text": "tiempo"}]}]),
            "an empty gloss list": entry(senses=[{"eng": ["weather"], "spa": []}]),
            "extra spaces": entry(senses=[{"eng": ["weather"], "spa": ["tiempo "]}]),
        }
        for what, e in cases.items():
            with self.subTest(what):
                self.assertNotEqual(run({"1002470": e}).errors, [])

    def test_style_rules_only_warn(self):
        report = run({"1002470": entry(senses=[{"eng": ["weather"], "spa": ["El tiempo."]},
                                               {"eng": ["mood", "temper"], "spa": ["humor", "hablando de ..."]}])})
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 3)        # an article, a capital, a full stop (not "...")

    def test_a_submission_must_match_todays_jmdict(self):
        stale = entry(senses=[{"eng": ["weather", "climate"], "spa": ["tiempo"]},
                              {"eng": ["mood", "temper"], "spa": ["humor"]}])
        self.assertNotEqual(run({"1002470": stale}, JMDICT).errors, [])
        self.assertNotEqual(run({"9999999": entry()}, JMDICT).errors, [])

    def test_an_approved_entry_whose_english_changed_is_flagged(self):
        stale = entry(status="approved", senses=[{"eng": ["weather", "climate"], "spa": ["tiempo"]},
                                                 {"eng": ["mood", "temper"], "spa": ["humor"]}])
        report = run({"1002470": stale}, JMDICT)
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 1)

    def test_layout(self):
        self.assertNotEqual(run({"1002470": entry()}, layout=False).errors, [])

    # A missing or extra newline at the end of the file is not a layout error
    def test_the_file_ending_does_not_matter(self):
        text = check.dump({"format": 1, "entries": {"1002470": entry()}})
        for ending in ("", "\n\n", "\n  \n"):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "spa.json"
                path.write_text(text.rstrip() + ending, encoding="utf-8")
                report = check.Report()
                check.check_file(report, path)
                self.assertEqual(report.errors, [], repr(ending))

    def test_file_names(self):
        self.assertEqual(run({}, name="spa_machine.json").errors, [])
        self.assertNotEqual(run({}, name="spanish.json").errors, [])

    def test_machine_translations_are_pending_and_marked(self):
        machine = entry(source="machine")
        self.assertEqual(run({"1002470": machine}, JMDICT, name="spa_machine.json").errors, [])
        for wrong in (entry(), entry(source="machine", status="approved")):
            self.assertNotEqual(run({"1002470": wrong}, name="spa_machine.json").errors, [])
        # A machine translation from before JMdict changed: to translate again, not a failure
        stale = entry(source="machine", senses=[{"eng": ["weather", "climate"], "spa": ["tiempo"]},
                                                {"eng": ["mood", "temper"], "spa": ["humor"]}])
        report = run({"1002470": stale}, JMDICT, name="spa_machine.json")
        self.assertEqual((report.errors, len(report.warnings)), ([], 1))

    def test_leftover_machine_translations_are_flagged(self):
        report = check.Report()
        check.check_leftovers(report, {"spa.json": {"1002470": entry(status="approved")},
                                       "spa_machine.json": {"1002470": entry(source="machine")}})
        self.assertEqual(len(report.warnings), 1)


class WordTest(unittest.TestCase):
    def test_every_entry_has_its_word(self):
        e = entry()
        del e["word"]
        self.assertNotEqual(run({"1002470": e}).errors, [])

    def test_a_word_jmdict_no_longer_uses_is_flagged(self):
        report = run({"1002470": entry(word="御天気【おてんき】")}, JMDICT)
        self.assertEqual((report.errors, len(report.warnings)), ([], 1))

    def test_headword(self):
        word = lambda kanji, kana: {"kanji": [{"text": k} for k in kanji],
                                    "kana": [{"text": t, "appliesToKanji": a} for t, a in kana]}
        self.assertEqual(check.headword(word(["お天気"], [("おてんき", ["*"])])), "お天気【おてんき】")
        self.assertEqual(check.headword(word([], [("しまった", ["*"])])), "しまった")
        # The first reading that applies to the first written form
        self.assertEqual(check.headword(word(["上手"], [("うわて", ["上手い"]), ("じょうず", ["上手"])])),
                         "上手【じょうず】")

    def test_the_layout_puts_the_word_first(self):
        e = entry()
        del e["word"]
        e["word"] = "お天気【おてんき】"
        text = check.dump({"format": 1, "entries": {"1002470": e}})
        self.assertLess(text.index('"word"'), text.index('"senses"'))


class PromoteTest(unittest.TestCase):
    def test_promote_and_clear(self):
        import promote
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            (data / "spa.json").write_text(check.dump({"format": 1, "entries": {
                "1": entry(status="approved")}}), encoding="utf-8")
            (data / "spa_machine.json").write_text(check.dump({"format": 1, "entries": {
                "1": entry(source="machine"), "2": entry(source="machine"), "3": entry(source="machine")}}),
                encoding="utf-8")
            promote.DATA = data
            promote.main(["spa", "2"])
            promote.main(["spa", "--approved"])
            main = json.loads((data / "spa.json").read_text(encoding="utf-8"))["entries"]
            machine = json.loads((data / "spa_machine.json").read_text(encoding="utf-8"))["entries"]
            self.assertEqual((sorted(main), main["2"]["status"], sorted(machine)), (["1", "2"], "pending", ["3"]))


if __name__ == "__main__":
    unittest.main()

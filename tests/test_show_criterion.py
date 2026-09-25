"""Checks for cross-edition meaning and omissions in criterion lookup."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from show_criterion import compact_lookup, lookup  # noqa: E402


class ShowCriterionTests(unittest.TestCase):
    def test_246_has_distinct_editions_and_both_understanding_sources(self) -> None:
        result = lookup("2.4.6")
        self.assertEqual([item["key"] for item in result["editions"]], [
            "wcag:2.2:2.4.6", "wcag:2.1:2.4.6", "wcag:2.0:2.4.6",
            "jis-x-8341-3:2016:2.4.6",
        ])
        self.assertEqual(len(result["relations"]), 3)
        self.assertEqual({page["language"] for page in result["understanding"]},
                         {"en", "ja"})
        japanese = result["editions"][0]["texts"][1]
        self.assertEqual(japanese["text"], "見出し及びラベルは、主題又は目的を説明している。")
        self.assertNotIn("html", japanese)
        self.assertEqual(result["editions"][-1]["texts"], [])

    def test_obsolete_and_new_criteria_are_not_inferred_for_other_editions(self) -> None:
        obsolete = lookup("4.1.1")
        self.assertEqual(obsolete["editions"][0]["status"], "obsolete_in_2.2")
        self.assertTrue(obsolete["editions"][0]["texts"][0]["text"].startswith("Note This"))
        self.assertTrue(obsolete["editions"][0]["texts"][1]["text"].startswith("注記 この"))
        self.assertIn("removed_in_later_edition",
                      {relation["relation"] for relation in obsolete["relations"]})
        new = lookup("2.5.8")
        self.assertEqual(len(new["editions"]), 1)
        self.assertEqual(new["relations"], [])

    def test_cli_json_and_bad_number(self) -> None:
        command = [sys.executable, str(ROOT / "tools/show_criterion.py")]
        result = subprocess.run(command + ["2.4.6", "--format", "json"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["number"], "2.4.6")
        invalid = subprocess.run(command + ["2.4"], capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("達成基準番号", invalid.stderr)

    def test_compact_lookup_preserves_translation_and_source(self) -> None:
        result = compact_lookup(lookup("2.4.6"), "wcag:2.2", "ja")
        self.assertEqual(result["item_key"], "wcag:2.2:2.4.6")
        self.assertEqual(result["level"], "AA")
        self.assertEqual(result["names"][0]["status"], "reference_translation")
        self.assertEqual(result["texts"][0]["text"],
                         "見出し及びラベルは、主題又は目的を説明している。")
        self.assertTrue(result["texts"][0]["source_ref"].startswith("https://waic.jp/"))
        self.assertEqual(result["sources"][0]["status"], "参考訳。正式版はW3Cの英語版")
        self.assertNotIn("understanding", result)
        self.assertNotIn("relations", result)

    def test_compact_lookup_does_not_invent_jis_text_or_missing_edition(self) -> None:
        result = compact_lookup(lookup("2.4.6"), "jis-x-8341-3:2016", "ja")
        self.assertEqual(result["texts"], [])
        self.assertEqual(result["names"][0]["status"], "workbook_label")
        self.assertEqual(result["sources"][0]["publication_status"],
                         "private_input; provenance_unverified")
        with self.assertRaises(LookupError):
            compact_lookup(lookup("2.5.8"), "jis-x-8341-3:2016", "ja")

    def test_cli_compact_json_requires_edition_and_language(self) -> None:
        command = [sys.executable, str(ROOT / "tools/show_criterion.py")]
        result = subprocess.run(command + ["2.4.6", "--format", "compact-json",
                                           "--edition", "wcag:2.2", "--language", "ja"],
                                capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["language"], "ja")
        missing = subprocess.run(command + ["2.4.6", "--format", "compact-json"],
                                 capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)
        self.assertIn("--edition", missing.stderr)


if __name__ == "__main__":
    unittest.main()

"""Checks for cross-edition meaning and omissions in criterion lookup."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from show_criterion import lookup  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()

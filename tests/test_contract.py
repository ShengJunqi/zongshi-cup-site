# -*- coding: utf-8 -*-
"""契约校验测试：有效夹具通过，无效夹具必须失败。"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from prepare_data import build, validate  # noqa: E402


class ContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.data = build()

    def test_valid_fixture(self) -> None:
        validate(self.data)

    def test_concept_date_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        d["events"][1]["public_start_at"] = "2026-11-01"
        with self.assertRaises(ValueError):
            validate(d)

    def test_missing_source_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        d["events"][0]["source_ref_id"] = "src_missing"
        with self.assertRaises(ValueError):
            validate(d)

    def test_bo_mismatch_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        m = d["matches"][0]
        m["format"] = "bo3"
        m["result"]["series_score"] = {"team_a_wins": 1, "team_b_wins": 1}
        m["result"]["status"] = "confirmed"
        with self.assertRaises(ValueError):
            validate(d)

    def test_win_mismatch_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        for st in d["player_game_stats"]:
            if st["team_id"] == "t_champ":
                st["win"] = False
                break
        with self.assertRaises(ValueError):
            validate(d)


if __name__ == "__main__":
    unittest.main()

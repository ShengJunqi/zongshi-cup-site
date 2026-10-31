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

    def test_bo_draw_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        m = d["matches"][0]
        m["result"]["series_score"] = {"team_a_wins": 1, "team_b_wins": 1}
        with self.assertRaises(ValueError):
            validate(d)

    def test_negative_wins_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        d["matches"][0]["result"]["series_score"] = {"team_a_wins": -1, "team_b_wins": 2}
        with self.assertRaises(ValueError):
            validate(d)

    def test_winner_side_mismatch_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        d["matches"][0]["result"]["winner_team_id"] = "t_osu"
        with self.assertRaises(ValueError):
            validate(d)

    def test_phase_ruleset_missing_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        d["phases"][0]["ruleset_id"] = "missing_ruleset"
        with self.assertRaises(ValueError):
            validate(d)

    def test_valid_pending_bo(self) -> None:
        d = copy.deepcopy(self.data)
        m = d["matches"][0]
        m["format"] = "bo3"
        m["result"] = {"winner_team_id": None,
                       "series_score": {"team_a_wins": 1, "team_b_wins": 0},
                       "status": "pending"}
        validate(d)

    def test_valid_bo3_2_1(self) -> None:
        d = copy.deepcopy(self.data)
        m = d["matches"][0]
        m["format"] = "bo3"
        m["result"] = {"winner_team_id": "t_osu",
                       "series_score": {"team_a_wins": 2, "team_b_wins": 1},
                       "status": "confirmed"}
        validate(d)

    def test_valid_bo5_3_2(self) -> None:
        d = copy.deepcopy(self.data)
        m = d["matches"][0]
        m["format"] = "bo5"
        m["result"] = {"winner_team_id": "t_champ",
                       "series_score": {"team_a_wins": 2, "team_b_wins": 3},
                       "status": "confirmed"}
        validate(d)

    def test_boolean_wins_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        d["matches"][0]["result"]["series_score"] = {"team_a_wins": True, "team_b_wins": 0}
        with self.assertRaises(ValueError):
            validate(d)

    def test_float_wins_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        d["matches"][0]["result"]["series_score"] = {"team_a_wins": 1.0, "team_b_wins": 0}
        with self.assertRaises(ValueError):
            validate(d)

    def test_pending_at_cap_rejected(self) -> None:
        d = copy.deepcopy(self.data)
        m = d["matches"][0]
        m["format"] = "bo3"
        m["result"] = {"winner_team_id": None,
                       "series_score": {"team_a_wins": 2, "team_b_wins": 0},
                       "status": "pending"}
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

# -*- coding: utf-8 -*-
"""按 docs/04 数据契约 v0.3 生成 M1 样板数据（data/site_data.json）。

数据来源：
- 赏金赛第一把：HOK-model/exports/website/players_combined.json（S2 十人结算 KDA/参团）
- 击杀/推塔时间线：同上 kills/towers；时间码冲突项标 pending
- 事件/来源/规则集/公告：docs/01、02、04 与事实台账（外部）
本脚本只读外部文件，不改动它们。生成失败时应报错而不是静默。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"D:\宗师杯视频\HOK-model\exports\website\players_combined.json")
OUT = ROOT / "data" / "site_data.json"

# 外部来源（locator 写相对项目名，公开页不暴露本机绝对路径）
SOURCES = [
    {"source_id": "src_settle_919", "kind": "screenshot", "locator": "赏金赛第一把 结算面板（视频 919s）",
     "source_date": None, "captured_at": "2026-10-28", "verified_status": "confirmed",
     "notes": "比分 3:17、十人 KDA/参团"},
    {"source_id": "src_identity_v01", "kind": "document", "locator": "身份与事实修正 v01 §2.1 / 十人身份核对 v02",
     "source_date": None, "captured_at": None, "verified_status": "partial",
     "notes": "一血与第一头时间存在两套记录；分路为候选"},
    {"source_id": "src_rules_20261008", "kind": "document", "locator": "比赛规则.docx（2026-10-08 版）",
     "source_date": "2026-10-08", "captured_at": None, "verified_status": "confirmed",
     "notes": "历史赏金赛规则；与未来赏金赛不是同一套规则"},
    {"source_id": "src_fact_ledger", "kind": "document", "locator": "00_事实台账.md（2026-10-28 版）",
     "source_date": "2026-10-28", "captured_at": None, "verified_status": "partial",
     "notes": "F26 速通 2.6×、F28 队内 MVP 额外 50%；金额不展示"},
    {"source_id": "src_mapkit", "kind": "document", "locator": "map_kit/README.md（地图教程例题）",
     "source_date": None, "captured_at": None, "verified_status": "partial",
     "notes": "推塔时间 B-B1≈04:01、B-B2≈04:28、B-M1≈05:23；需复核原帧"},
    {"source_id": "src_jason_20261031", "kind": "manual", "locator": "Jason 下一阶段任务大纲（2026-10-31）",
     "source_date": "2026-10-31", "captured_at": None, "verified_status": "confirmed",
     "notes": "赛事方向、A 主视觉、范围与协作边界"},
]

RULESETS = [
    {"ruleset_id": "bounty_2026_10", "version": "2026-10-08", "title": "赏金赛（历史）",
     "category": "bounty_event", "status": "historical", "source_ref_id": "src_rules_20261008"},
    {"ruleset_id": "bounty_auction_concept", "version": "0.0", "title": "赛季中赏金淘汰赛（构想）",
     "category": "bounty_event", "status": "concept", "source_ref_id": "src_jason_20261031"},
    {"ruleset_id": "to_be_decided", "version": "0.0", "title": "正式赛事规则集（待定）",
     "category": "formal_league", "status": "concept", "source_ref_id": "src_jason_20261031"},
]

EVENTS = [
    {"event_id": "e_s2_01", "title": "赏金赛第一把", "category": "bounty_event",
     "data_origin": "historical_export", "publish_status": "announced",
     "archive_status": "historical", "progress_status": "completed",
     "ruleset_id": "bounty_2026_10", "default_team_formation": "invited",
     "default_stage_format": "one_day", "default_match_format": "bo1",
     "public_schedule_status": "tbd", "public_start_at": None, "public_end_at": None,
     "internal_plan_note": None, "internal_planned_start_at": None,
     "summary": "历史单场；比赛日期待确认", "source_ref_id": "src_fact_ledger"},
    {"event_id": "e_league_concept", "title": "长周期正式赛事（筹备）", "category": "formal_league",
     "data_origin": "concept", "publish_status": "concept", "archive_status": "active",
     "progress_status": "tbd", "ruleset_id": "to_be_decided",
     "default_team_formation": "unknown", "default_stage_format": "unknown",
     "default_match_format": "unknown",
     "public_schedule_status": "tbd", "public_start_at": None, "public_end_at": None,
     "internal_plan_note": None, "internal_planned_start_at": None,
     "summary": "筹备方案，尚未公布", "source_ref_id": "src_jason_20261031"},
    {"event_id": "e_bounty_concept", "title": "赛季中赏金淘汰赛（筹备）", "category": "bounty_event",
     "data_origin": "concept", "publish_status": "concept", "archive_status": "active",
     "progress_status": "tbd", "ruleset_id": "bounty_auction_concept",
     "default_team_formation": "auction", "default_stage_format": "single_elim",
     "default_match_format": "unknown",
     "public_schedule_status": "tbd", "public_start_at": None, "public_end_at": None,
     "internal_plan_note": None, "internal_planned_start_at": None,
     "summary": "拍卖式组队为待设计构想，尚未公布；与历史赏金赛规则不同",
     "source_ref_id": "src_jason_20261031"},
]

PHASES = [
    {"phase_id": "ph_league_preseason", "event_id": "e_league_concept", "kind": "preseason",
     "order": 1, "window_status": "tbd", "stage_format": None, "match_format": None,
     "team_formation": None, "ruleset_id": None, "public_schedule_status": "tbd",
     "public_start_at": None, "public_end_at": None, "internal_plan_note": None,
     "source_ref_id": "src_jason_20261031"},
    {"phase_id": "ph_bounty_oneday", "event_id": "e_bounty_concept", "kind": "one_day",
     "order": 1, "window_status": "tbd", "stage_format": "single_elim", "match_format": None,
     "team_formation": "auction", "ruleset_id": None, "public_schedule_status": "tbd",
     "public_start_at": None, "public_end_at": None, "internal_plan_note": None,
     "source_ref_id": "src_jason_20261031"},
]

TEAMS = [
    {"team_id": "t_osu", "name": "OSU 学生擂主队", "team_status": "confirmed", "name_history": []},
    {"team_id": "t_champ", "name": "上届冠军队伍", "team_status": "candidate", "name_history": []},
]

ROLE_MAP = {
    "对抗路": "对抗路", "打野": "打野", "中路": "中路", "发育路": "发育路", "游走": "游走",
}


def load_s2() -> list[dict]:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    return data["s2"]


def build() -> dict:
    s2 = load_s2()
    persons, stats, snaps = [], [], {"t_osu": [], "t_champ": []}
    name_to_person = {}
    for i, row in enumerate(s2, start=1):
        pid = f"p_{i:04d}"
        name_to_person[row["name"]] = pid
        persons.append({"person_id": pid, "display_name": row["name"],
                        "identity_status": "candidate", "nickname_history": [],
                        "merged_into": None, "privacy_flags": []})
        team_id = "t_osu" if row["team"].startswith("我方") else "t_champ"
        k, d, a = (int(x) for x in row["kda_str"].split("/"))
        stats.append({"stat_id": f"pgs_{i:02d}", "game_id": "g_s2_01_1", "person_id": pid,
                      "team_id": team_id, "role": row["role"], "role_status": "candidate",
                      "kills": k, "deaths": d, "assists": a,
                      "participation": row["participation"], "win": False,
                      "source_ref_id": "src_settle_919", "verification_status": "confirmed"})
        snaps[team_id].append({"person_id": pid, "role": row["role"],
                               "role_status": "candidate", "joined_at": None})

    roster_snapshots = [
        {"snapshot_id": "rs_s2_osu_v1", "event_id": "e_s2_01", "phase_id": None,
         "team_id": "t_osu", "version": "v1", "created_at": None, "status": "candidate",
         "source_ref_id": "src_settle_919", "entries": snaps["t_osu"]},
        {"snapshot_id": "rs_s2_champ_v1", "event_id": "e_s2_01", "phase_id": None,
         "team_id": "t_champ", "version": "v1", "created_at": None, "status": "candidate",
         "source_ref_id": "src_settle_919", "entries": snaps["t_champ"]},
    ]

    match = {"match_id": "m_s2_01", "event_id": "e_s2_01", "phase_id": None, "round": None,
             "bracket_slot": None, "team_a_id": "t_osu", "team_b_id": "t_champ", "format": "bo1",
             "team_a_roster_snapshot_id": "rs_s2_osu_v1",
             "team_b_roster_snapshot_id": "rs_s2_champ_v1",
             "public_schedule_status": "tbd", "public_scheduled_start": None,
             "result": {"winner_team_id": "t_champ",
                        "series_score": {"team_a_wins": 0, "team_b_wins": 1},
                        "status": "confirmed"}}

    game = {"game_id": "g_s2_01_1", "match_id": "m_s2_01", "game_no": 1,
            "winner_team_id": "t_champ", "team_kills": {"team_a": 3, "team_b": 17},
            "duration_clock": "06:03", "stats_status": "partial",
            "actual_team_a_roster_snapshot_id": None,
            "actual_team_b_roster_snapshot_id": None, "source_ref_id": "src_settle_919"}

    attacks = name_to_person.get("放闪的秋")
    timeline = [
        {"timeline_id": "tl_kill_01", "game_id": "g_s2_01_1", "clock": "00:44",
         "clock_status": "pending", "type": "kill", "team_id": "t_champ", "person_id": None,
         "attribution_status": "unknown",
         "description": "敌方一血（时间口径 00:41/00:44 待统一）",
         "evidence_ref_id": "src_identity_v01"},
        {"timeline_id": "tl_kill_02", "game_id": "g_s2_01_1", "clock": "01:53",
         "clock_status": "confirmed", "type": "kill", "team_id": "t_champ", "person_id": None,
         "attribution_status": "unknown", "description": "敌方连续击杀，比分 0:4",
         "evidence_ref_id": "src_identity_v01"},
        {"timeline_id": "tl_kill_03", "game_id": "g_s2_01_1", "clock": "01:57",
         "clock_status": "pending", "type": "kill", "team_id": "t_osu", "person_id": attacks,
         "attribution_status": "known",
         "description": "全队第一头（放闪的秋·铠；时间口径 01:56/01:57 待统一）",
         "evidence_ref_id": "src_identity_v01"},
        {"timeline_id": "tl_kill_04", "game_id": "g_s2_01_1", "clock": "03:23",
         "clock_status": "confirmed", "type": "kill", "team_id": "t_osu", "person_id": attacks,
         "attribution_status": "known", "description": "全队第二头（放闪的秋·铠）",
         "evidence_ref_id": "src_identity_v01"},
        {"timeline_id": "tl_kill_05", "game_id": "g_s2_01_1", "clock": "04:40",
         "clock_status": "confirmed", "type": "kill", "team_id": "t_osu", "person_id": attacks,
         "attribution_status": "known", "description": "全队第三头（放闪的秋·铠）",
         "evidence_ref_id": "src_identity_v01"},
        {"timeline_id": "tl_tower_01", "game_id": "g_s2_01_1", "clock": "04:01",
         "clock_status": "pending", "type": "tower", "team_id": None, "person_id": None,
         "attribution_status": "unknown", "description": "蓝方下路外塔 B-B1 失守（教程例题，需复核原帧）",
         "evidence_ref_id": "src_mapkit"},
        {"timeline_id": "tl_tower_02", "game_id": "g_s2_01_1", "clock": "04:28",
         "clock_status": "pending", "type": "tower", "team_id": None, "person_id": None,
         "attribution_status": "unknown", "description": "蓝方下路二塔 B-B2 出现摧毁提示",
         "evidence_ref_id": "src_mapkit"},
        {"timeline_id": "tl_tower_03", "game_id": "g_s2_01_1", "clock": "05:23",
         "clock_status": "pending", "type": "tower", "team_id": None, "person_id": None,
         "attribution_status": "unknown", "description": "蓝方中路外塔 B-M1 失守（约 05:16 出现提示）",
         "evidence_ref_id": "src_mapkit"},
        {"timeline_id": "tl_base_01", "game_id": "g_s2_01_1", "clock": "06:03",
         "clock_status": "confirmed", "type": "base", "team_id": "t_champ", "person_id": None,
         "attribution_status": "known", "description": "我方基地被摧毁（最后可见时钟）",
         "evidence_ref_id": "src_settle_919"},
    ]

    announcements = [
        {"announcement_id": "a_site_01", "event_id": None,
         "title": "M1 样板说明：这是结构与视觉样板",
         "body": "本页不是正式赛事公告；赛程、报名、奖金信息以主办方公布为准。样板只展示已核实事实与已审核内容。",
         "publish_status": "published", "date_status": "tbd", "published_at": None,
         "source_ref_id": "src_jason_20261031"},
        {"announcement_id": "a_s2_01", "event_id": "e_s2_01",
         "title": "赏金赛第一把：战报与数据已整理",
         "body": "结算 3:17、基地在 6:03 被摧毁；时间码与分路口径仍在核对，页面已标「待核实」。",
         "publish_status": "published", "date_status": "tbd", "published_at": None,
         "source_ref_id": "src_settle_919"},
        {"announcement_id": "a_league_draft", "event_id": "e_league_concept",
         "title": "长周期赛事筹备中（草案，未发布）",
         "body": "赛制、阶段、队伍与时间均待讨论，不对外发布。",
         "publish_status": "draft", "date_status": "tbd", "published_at": None,
         "source_ref_id": "src_jason_20261031"},
    ]

    return {"schema_version": "0.3", "sources": SOURCES, "rulesets": RULESETS,
            "persons": persons, "teams": TEAMS, "events": EVENTS, "phases": PHASES,
            "roster_snapshots": roster_snapshots, "matches": [match], "games": [game],
            "player_game_stats": stats, "timeline": timeline,
            "announcements": announcements}


def validate(data: dict) -> None:
    """最小引用与状态校验；失败抛异常（生成器必须执行）。"""
    src = {s["source_id"] for s in data["sources"]}
    rules = {r["ruleset_id"] for r in data["rulesets"]}
    persons = {p["person_id"] for p in data["persons"]}
    teams = {t["team_id"] for t in data["teams"]}
    events = {e["event_id"] for e in data["events"]}
    phases = {p["phase_id"] for p in data["phases"]}
    snaps = {s["snapshot_id"] for s in data["roster_snapshots"]}
    matches = {m["match_id"] for m in data["matches"]}
    games = {g["game_id"] for g in data["games"]}

    for e in data["events"]:
        assert e["source_ref_id"] in src, e["event_id"]
        assert e["ruleset_id"] in rules, e["event_id"]
        if e["publish_status"] == "concept":
            assert e["public_schedule_status"] == "tbd"
            assert e["public_start_at"] is None and e["public_end_at"] is None
    for p in data["phases"]:
        assert p["event_id"] in events and p["source_ref_id"] in src
    for s in data["roster_snapshots"]:
        assert s["event_id"] in events and s["team_id"] in teams and s["source_ref_id"] in src
        for en in s["entries"]:
            assert en["person_id"] in persons
    for m in data["matches"]:
        assert m["event_id"] in events
        assert m["team_a_id"] in teams and m["team_b_id"] in teams
        assert m["team_a_roster_snapshot_id"] in snaps
        assert m["team_b_roster_snapshot_id"] in snaps
        cap = {"bo1": 1, "bo3": 2, "bo5": 3, "bo7": 4}[m["format"]]
        sc = m["result"]["series_score"]
        assert max(sc["team_a_wins"], sc["team_b_wins"]) == cap, m["match_id"]
    for g in data["games"]:
        assert g["match_id"] in matches and g["source_ref_id"] in src
    for st in data["player_game_stats"]:
        assert st["game_id"] in games and st["person_id"] in persons
        assert st["team_id"] in teams and st["source_ref_id"] in src
    for t in data["timeline"]:
        assert t["game_id"] in games and t["evidence_ref_id"] in src
    for a in data["announcements"]:
        assert a["source_ref_id"] in src
        if a["event_id"]:
            assert a["event_id"] in events


if __name__ == "__main__":
    data = build()
    validate(data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {OUT}  ({OUT.stat().st_size} bytes)")

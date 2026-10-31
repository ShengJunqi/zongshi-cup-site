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
    {"source_id": "src_base_905", "kind": "video", "locator": "第一把录像 905s（最后可见时钟 06:03）",
     "source_date": None, "captured_at": None, "verified_status": "confirmed",
     "notes": "最后可见时钟；基地爆炸演出在其后"},
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
                      "participation": row["participation"], "win": team_id == "t_champ",
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
         "attribution_status": "known", "description": "我方基地被摧毁（最后可见时钟 6:03）",
         "evidence_ref_id": "src_base_905"},
    ]

    announcements = [
        {"announcement_id": "a_site_01", "event_id": None,
         "title": "M1 样板说明：这是结构与视觉样板",
         "body": "本页不是正式赛事公告；赛程、报名、奖金信息以主办方公布为准。样板只展示已核实事实与已审核内容。",
         "publish_status": "published", "date_status": "tbd", "published_at": None,
         "source_ref_id": "src_jason_20261031"},
        {"announcement_id": "a_s2_01", "event_id": "e_s2_01",
         "title": "赏金赛第一把：战报与数据已整理",
         "body": "结算 3:17、最后可见时钟 6:03（基地爆炸演出在其后）；时间码与分路口径仍在核对，页面已标「待核实」。",
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
    """契约校验；失败抛 ValueError（构建入口必须调用）。"""
    def need(cond, msg):
        if not cond:
            raise ValueError("contract violation: " + msg)

    src = {s["source_id"] for s in data["sources"]}
    rules = {r["ruleset_id"] for r in data["rulesets"]}
    persons = {p["person_id"] for p in data["persons"]}
    teams = {t["team_id"] for t in data["teams"]}
    events = {e["event_id"] for e in data["events"]}
    phases = {p["phase_id"] for p in data["phases"]}
    snaps = {s["snapshot_id"]: s for s in data["roster_snapshots"]}
    matches = {m["match_id"]: m for m in data["matches"]}
    games = {g["game_id"]: g for g in data["games"]}
    by_game = {}

    need(data.get("schema_version") == "0.3", "schema_version")
    for s in data["sources"]:
        need(s["kind"] in {"screenshot", "video", "spreadsheet", "document", "manual", "api"}, "source kind " + s["source_id"])
        need(s["verified_status"] in {"confirmed", "partial", "unverified"}, "source status " + s["source_id"])
    for r in data["rulesets"]:
        need(r["status"] in {"historical", "concept", "announced"}, "ruleset status " + r["ruleset_id"])
        need(r["source_ref_id"] in src, "ruleset source " + r["ruleset_id"])
    for e in data["events"]:
        need(e["publish_status"] in {"concept", "pending", "announced"}, "publish " + e["event_id"])
        need(e["archive_status"] in {"active", "historical", "archived"}, "archive " + e["event_id"])
        need(e["progress_status"] in {"tbd", "scheduled", "live", "completed", "cancelled"}, "progress " + e["event_id"])
        need(e["category"] in {"formal_league", "bounty_event", "ranked_night", "other"}, "category " + e["event_id"])
        need(e["data_origin"] in {"official", "historical_export", "concept", "demo"}, "data_origin " + e["event_id"])
        need(e["source_ref_id"] in src, "event source " + e["event_id"])
        need(e["ruleset_id"] in rules, "event ruleset " + e["event_id"])
        need(e["public_schedule_status"] in {"confirmed", "tbd"}, "event schedule " + e["event_id"])
        if e["publish_status"] == "concept" or e["public_schedule_status"] == "tbd":
            need(e["public_start_at"] is None and e["public_end_at"] is None, "concept/tbd dates " + e["event_id"])
    for p in data["phases"]:
        need(p["event_id"] in events, "phase event " + p["phase_id"])
        need(p["kind"] in {"preseason", "regular", "playoffs", "one_day", "qualifier", "other"}, "phase kind " + p["phase_id"])
        need(p["public_schedule_status"] in {"confirmed", "tbd"}, "phase schedule " + p["phase_id"])
        need(p["source_ref_id"] in src, "phase source " + p["phase_id"])
        if p.get("ruleset_id") is not None:
            need(p["ruleset_id"] in rules, "phase ruleset " + p["phase_id"])
    for sid, s in snaps.items():
        need(s["event_id"] in events, "snapshot event " + sid)
        need(s["team_id"] in teams, "snapshot team " + sid)
        need(s["status"] in {"confirmed", "candidate", "superseded"}, "snapshot status " + sid)
        need(s["source_ref_id"] in src, "snapshot source " + sid)
        for en in s["entries"]:
            need(en["person_id"] in persons, "snapshot person " + sid)
            need(en["role_status"] in {"confirmed", "candidate", "unknown"}, "snapshot role status " + sid)
    for mid, m in matches.items():
        need(m["event_id"] in events, "match event " + mid)
        need(m["team_a_id"] in teams and m["team_b_id"] in teams, "match teams " + mid)
        need(m["team_a_roster_snapshot_id"] in snaps and m["team_b_roster_snapshot_id"] in snaps, "match rosters " + mid)
        need(m["format"] in {"bo1", "bo3", "bo5", "bo7"}, "match format " + mid)
        if m.get("phase_id") is not None:
            need(m["phase_id"] in phases, "match phase " + mid)
        cap = {"bo1": 1, "bo3": 2, "bo5": 3, "bo7": 4}[m["format"]]
        res = m["result"]
        need(res["status"] in {"pending", "confirmed"}, "match result status " + mid)
        a, b = res["series_score"]["team_a_wins"], res["series_score"]["team_b_wins"]
        need(type(a) is int and type(b) is int and a >= 0 and b >= 0, "BO wins int/non-negative " + mid)
        if res["status"] == "confirmed":
            need((a == cap and b < cap) or (b == cap and a < cap), "confirmed BO winner " + mid)
            need(res.get("winner_team_id") in teams, "confirmed match winner " + mid)
            if a == cap:
                need(res["winner_team_id"] == m["team_a_id"], "winner side A " + mid)
            else:
                need(res["winner_team_id"] == m["team_b_id"], "winner side B " + mid)
        else:
            need(a < cap and b < cap, "pending BO result " + mid)
    for gid, g in games.items():
        mid = g["match_id"]
        need(mid in matches, "game match " + gid)
        need(g["source_ref_id"] in src, "game source " + gid)
        need(g["stats_status"] in {"complete", "partial", "pending"}, "game stats status " + gid)
        need(g["team_kills"]["team_a"] >= 0 and g["team_kills"]["team_b"] >= 0, "game kills " + gid)
        need(g["team_kills"]["team_a"] != g["team_kills"]["team_b"], "game draw kills " + gid)
        if g["winner_team_id"] is not None:
            need(g["winner_team_id"] in {matches[mid]["team_a_id"], matches[mid]["team_b_id"]}, "game winner " + gid)
            ka, kb = g["team_kills"]["team_a"], g["team_kills"]["team_b"]
            need((g["winner_team_id"] == matches[mid]["team_a_id"] and ka > kb) or
                 (g["winner_team_id"] == matches[mid]["team_b_id"] and kb > ka), "game winner vs kills " + gid)
        for key in ("actual_team_a_roster_snapshot_id", "actual_team_b_roster_snapshot_id"):
            if g.get(key):
                need(g[key] in snaps, "game roster " + gid)
    for mid, m in matches.items():
        gs = [g for g in games.values() if g["match_id"] == mid and g.get("winner_team_id")]
        a_wins = m["result"]["series_score"]["team_a_wins"]
        b_wins = m["result"]["series_score"]["team_b_wins"]
        if m["result"]["status"] == "confirmed" and gs and len(gs) == a_wins + b_wins:
            wa = sum(1 for g in gs if g["winner_team_id"] == m["team_a_id"])
            wb = sum(1 for g in gs if g["winner_team_id"] == m["team_b_id"])
            need(wa == m["result"]["series_score"]["team_a_wins"] and wb == m["result"]["series_score"]["team_b_wins"],
                 "series vs games " + mid)
    for st in data["player_game_stats"]:
        g = games[st["game_id"]]
        need(st["person_id"] in persons and st["team_id"] in teams, "stat refs " + st["stat_id"])
        need(st["source_ref_id"] in src, "stat source " + st["stat_id"])
        need(st["role_status"] in {"confirmed", "candidate", "unknown"}, "stat role status " + st["stat_id"])
        need(st["verification_status"] in {"confirmed", "unverified", "disputed"}, "stat verify " + st["stat_id"])
        if g.get("winner_team_id"):
            need(st["win"] == (st["team_id"] == g["winner_team_id"]), "stat win mismatch " + st["stat_id"])
        by_game.setdefault(st["game_id"], []).append(st)
    for t in data["timeline"]:
        need(t["game_id"] in games, "timeline game " + t["timeline_id"])
        need(t["type"] in {"kill", "tower", "objective", "base"}, "timeline type " + t["timeline_id"])
        need(t["clock_status"] in {"confirmed", "pending"}, "timeline clock " + t["timeline_id"])
        need(t["attribution_status"] in {"known", "unknown"}, "timeline attribution " + t["timeline_id"])
        need(t["evidence_ref_id"] in src, "timeline evidence " + t["timeline_id"])
    for a in data["announcements"]:
        need(a["publish_status"] in {"draft", "published"}, "announcement status " + a["announcement_id"])
        need(a["date_status"] in {"confirmed", "tbd"}, "announcement date " + a["announcement_id"])
        need(a["source_ref_id"] in src, "announcement source " + a["announcement_id"])
        if a["event_id"]:
            need(a["event_id"] in events, "announcement event " + a["announcement_id"])


if __name__ == "__main__":
    data = build()
    validate(data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {OUT}  ({OUT.stat().st_size} bytes)")

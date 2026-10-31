# -*- coding: utf-8 -*-
"""把 data/site_data.json 渲染成 M1 A 风格静态样板（site/）。

规则：
- 未确认状态必须显示「待核实/待确认」，不能只显示数值；
- concept 赛事显示「筹备方案，尚未公布」，不显示日期/报名/奖金；
- 历史与未来赏金赛分开，S1/S2 不写成正式赛季；
- 不嵌入未授权视频，视频区只留占位；
- 不批量生成选手页，本轮只有 1 个样板选手页。
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "site_data.json"
SITE = ROOT / "site"
SAMPLE_SLUG = "fangshan-de-qiu"

CSS = r"""
:root{--bg:#0a0d14;--panel:#121826;--panel2:#0e1320;--gold:#e8a832;--gold2:#f6cf7a;--text:#eef1f6;--muted:#aab1c2;--line:#263044;--ok:#7fd6a0;--warn:#f2b95c;--danger:#ff8f80;--blue:#6fa8ff}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:radial-gradient(120% 55% at 50% 0%,#231d10 0%,#0a0d14 58%) no-repeat,var(--bg);color:var(--text);font-family:"Noto Sans SC","Microsoft YaHei","PingFang SC",system-ui,sans-serif;font-size:15.5px;line-height:1.7;-webkit-text-size-adjust:100%}
a{color:var(--gold2);text-decoration:none}
a:hover{text-decoration:underline}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.wrap{max-width:1060px;margin:0 auto;padding:0 16px 104px}
.topbar{position:sticky;top:0;z-index:20;background:rgba(10,13,20,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.topbar-in{max-width:1060px;margin:0 auto;padding:0 16px;display:flex;align-items:center;gap:10px}
.brand{display:flex;align-items:center;gap:10px;padding:9px 0;min-width:0}
.seal{width:38px;height:38px;flex:none;border:2px solid var(--gold);border-radius:8px;display:grid;place-items:center;font:700 18px/1 "STKaiti","KaiTi",serif;color:var(--gold)}
.brand b{font-size:18px;letter-spacing:2px;display:block;line-height:1.15}
.brand span{display:block;font-size:12px;color:var(--muted);letter-spacing:.4px}
.nav{display:flex;gap:4px;margin-left:auto}
.nav a{display:flex;align-items:center;min-height:44px;padding:0 12px;font-size:14.5px;color:var(--muted);border-radius:8px}
.nav a.on{color:var(--gold);background:rgba(232,168,50,.1)}
.mobile-nav{display:none}
.hero{padding:38px 0 20px}
.eyebrow{font-size:12.5px;letter-spacing:3px;color:var(--gold)}
h1{font-size:clamp(30px,6.4vw,46px);margin:8px 0 8px;letter-spacing:1px;line-height:1.25}
h2{font-size:21px;margin:0 0 10px}
h3{font-size:16.5px;margin:0 0 6px}
.lead{font-size:16.5px;color:#d9dde6;max-width:780px;margin:8px 0 14px}
.muted{color:var(--muted)}
.small{font-size:14px;color:#b9c0cf;line-height:1.75}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 0}
.badge{display:inline-flex;align-items:center;gap:5px;border:1px solid var(--line);border-radius:999px;padding:3px 10px;font-size:12.5px;color:var(--muted);white-space:nowrap}
.badge.gold{color:var(--gold);border-color:rgba(232,168,50,.42);background:rgba(232,168,50,.08)}
.badge.ok{color:var(--ok);border-color:rgba(127,214,160,.35);background:rgba(127,214,160,.08)}
.badge.warn{color:var(--warn);border-color:rgba(242,185,92,.38);background:rgba(242,185,92,.08)}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:9px 18px;border-radius:10px;background:var(--gold);color:#151007;font-weight:700;font-size:15px;border:1px solid var(--gold)}
.btn:hover{text-decoration:none;filter:brightness(1.06)}
.btn.ghost{background:transparent;color:var(--gold2);border-color:rgba(232,168,50,.5)}
.btn.small{min-height:44px;padding:8px 14px;font-size:14px}
.hero-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:16px}
.grid{display:grid;gap:14px}
.cols2{grid-template-columns:repeat(2,1fr)}
.cols3{grid-template-columns:repeat(3,1fr)}
.card{background:linear-gradient(165deg,rgba(20,26,38,.96),rgba(13,18,28,.96));border:1px solid var(--line);border-radius:14px;padding:18px}
.card.tight{padding:14px 16px}
.section{margin-top:34px}
.section-head{display:flex;align-items:baseline;justify-content:space-between;gap:12px;margin-bottom:12px}
.section-head h2{margin:0;border-left:4px solid var(--gold);padding-left:10px}
.section-head a{font-size:14px;white-space:nowrap}
.score{font-family:Consolas,ui-monospace,monospace;font-size:clamp(34px,8vw,52px);letter-spacing:2px;line-height:1.05;margin:4px 0 6px}
.score .lose{color:var(--danger)}
.score-label{font-size:12.5px;color:var(--gold);letter-spacing:2px}
.kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(118px,1fr));gap:10px}
.kv .item{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.kv .item span{display:block;font-size:12px;color:var(--muted)}
.kv .item b{font-size:18px;font-family:Consolas,monospace;color:var(--gold2)}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px}
table{width:100%;border-collapse:collapse;font-size:14px;min-width:520px}
th,td{padding:10px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
tr:last-child td{border-bottom:none}
th{color:var(--gold);font-weight:600;font-size:13px;background:rgba(232,168,50,.05);white-space:nowrap}
.src{display:inline-block;font-size:12px;color:#b9c0cf;padding:12px 10px;margin:-12px -10px;text-decoration:underline;text-underline-offset:2px;white-space:nowrap}
.status{display:inline-block;font-size:12px;border-radius:999px;padding:1px 8px;margin-left:6px;white-space:nowrap;border:1px solid var(--line)}
.status.pending{color:var(--warn);border-color:rgba(242,185,92,.4);background:rgba(242,185,92,.08)}
.status.candidate{color:var(--warn);border-color:rgba(242,185,92,.4);background:rgba(242,185,92,.08)}
.status.confirmed{color:var(--ok);border-color:rgba(127,214,160,.35);background:rgba(127,214,160,.08)}
.timeline{list-style:none;margin:6px 0 0;padding:0}
.timeline li{display:flex;gap:12px;padding:10px 0;border-top:1px dashed var(--line);font-size:14px}
.timeline li:first-child{border-top:none}
.timeline time{font-family:Consolas,monospace;color:var(--gold2);min-width:58px;flex:none}
.note{background:rgba(232,168,50,.06);border-left:3px solid var(--gold);border-radius:8px;padding:12px 14px;font-size:14px;color:#dde1e9;margin:12px 0}
.notice{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:var(--panel2);font-size:14px;color:#d7dbe4;margin:10px 0}
.breadcrumb{font-size:13px;color:var(--muted);margin:18px 0 0}
.breadcrumb a{color:var(--muted)}
.player-head{display:flex;flex-wrap:wrap;align-items:center;gap:14px;padding:18px 0 4px}
.avatar{width:64px;height:64px;flex:none;border-radius:14px;border:1px solid rgba(232,168,50,.4);background:radial-gradient(circle at 30% 20%,rgba(232,168,50,.35),rgba(20,26,38,.95));display:grid;place-items:center;font:700 22px/1 "STKaiti","KaiTi",serif;color:var(--gold)}
.player-head h1{font-size:clamp(26px,7vw,40px);margin:0;line-height:1.15}
.tag{display:inline-block;font-size:12px;color:var(--muted);border:1px dashed var(--line);border-radius:999px;padding:2px 9px;margin:4px 6px 0 0}
.switcher{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}
.switcher a{font-size:12.5px;border:1px solid var(--line);border-radius:999px;padding:2px 9px;color:var(--muted)}
.switcher a.on{color:var(--gold);border-color:rgba(232,168,50,.45);background:rgba(232,168,50,.08)}
.footer{margin-top:44px;border-top:1px solid var(--line);padding-top:18px;font-size:13px;color:var(--muted);line-height:1.9}
.footer a{color:var(--muted)}
details{border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:var(--panel2);margin-top:10px}
summary{cursor:pointer;font-size:14px;color:var(--gold2)}
.scroll-hint{display:none;font-size:13px;color:var(--warn);margin:6px 0 0}
@media(max-width:760px){.scroll-hint{display:block}}
.videoph{aspect-ratio:16/9;border:1px dashed var(--line);border-radius:12px;display:grid;place-items:center;text-align:center;padding:16px;color:var(--muted);font-size:13.5px;background:linear-gradient(140deg,rgba(232,168,50,.05),transparent)}
.sharebox{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px;align-items:center}
.copy-hint{font-size:12.5px;color:var(--ok)}
@media(max-width:760px){
 .wrap{padding:0 14px 96px}
 .nav{display:none}
 .mobile-nav{display:grid;grid-template-columns:repeat(4,1fr);position:fixed;bottom:0;left:0;right:0;z-index:30;background:#0b0f18;border-top:1px solid var(--line);padding:2px 4px calc(2px + env(safe-area-inset-bottom))}
 .mobile-nav a{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:52px;font-size:12.5px;color:var(--muted);gap:0}
 
 .mobile-nav a.on{color:var(--gold)}
 .cols2,.cols3{grid-template-columns:1fr}
 .card{padding:15px}
 .hero{padding:26px 0 12px}
 .lead{font-size:15.5px}
}
@media(max-width:360px){
 .brand b{font-size:16px}.brand span{display:none}
 .hero-actions .btn{width:100%}
}
"""


def esc(s) -> str:
    return html.escape(str(s if s is not None else ""))


def fmt_num(v) -> str:
    if v is None:
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return esc(str(v))
    return str(int(f)) if f == int(f) else ("%.1f" % f)


PHASE_KIND = {"preseason": "赛前筹备", "regular": "常规赛", "playoffs": "季后赛",
              "one_day": "单日赛", "qualifier": "资格赛", "other": "其他"}


class Site:
    def __init__(self, data: dict):
        self.d = data
        self.sources = {s["source_id"]: s for s in data["sources"]}
        self.persons = {p["person_id"]: p for p in data["persons"]}
        self.teams = {t["team_id"]: t for t in data["teams"]}
        self.events = {e["event_id"]: e for e in data["events"]}
        self.public_events = {eid: e for eid, e in self.events.items()
                              if e["archive_status"] != "archived"}
        self.phases = {p["phase_id"]: p for p in data["phases"]}
        self.matches = {m["match_id"]: m for m in data["matches"]}
        self.games = {g["game_id"]: g for g in data["games"]}
        self.stats = data["player_game_stats"]
        self.timeline = data["timeline"]
        self.announcements = data["announcements"]
        self.rulesets = {r["ruleset_id"]: r for r in data["rulesets"]}

    # ---------- helpers ----------
    def src(self, sid: str, label: str = "来源") -> str:
        s = self.sources.get(sid)
        if not s:
            return ""
        title = f'{s["locator"]} · {s.get("verified_status","")}'
        return f'<a class="src" href="{self.prefix}sources.html#{esc(sid)}" title="{esc(title)}">{esc(label)}</a>'

    def status(self, value: str, kind: str | None = None) -> str:
        kind = kind or value
        label = {"pending": "待核实", "candidate": "待确认", "confirmed": "已确认",
                 "partial": "部分确认", "unverified": "待核实", "draft": "草稿",
                 "tbd": "待公布", "concept": "筹备（未公布）", "historical": "历史",
                 "announced": "已公布"}.get(value, value)
        cls = "pending" if value in ("pending", "unverified", "partial", "tbd", "concept") else (
            "candidate" if value == "candidate" else "confirmed")
        return f'<span class="status {cls}">{esc(label)}</span>'

    def event_state(self, e: dict) -> str:
        if e["publish_status"] == "concept":
            return '<span class="badge warn">筹备方案，尚未公布</span>'
        if e["archive_status"] == "historical" and e["progress_status"] == "completed":
            return '<span class="badge">历史赛事 · 已结束</span>'
        if e["progress_status"] == "completed":
            return '<span class="badge">已结束</span>'
        return '<span class="badge gold">待公布</span>'

    def date_text(self, e: dict) -> str:
        if e["publish_status"] == "concept":
            return "赛程待公布（筹备方案，不显示日期）"
        if e["public_schedule_status"] != "confirmed":
            return "日期待确认"
        return f'{e["public_start_at"] or ""}'

    def clock_note(self) -> str:
        g = self.games["g_s2_01_1"]
        return f"最后可见时钟 {g['duration_clock']}（基地爆炸演出在其后）"

    def highlight_text(self) -> str:
        ts = [t for t in self.timeline if t["type"] == "kill" and t["person_id"] == "p_0002"]
        parts = []
        for t in ts:
            parts.append(("约 " + t["clock"] + "（待核实）") if t["clock_status"] != "confirmed" else t["clock"])
        return " / ".join(parts) if parts else "—"

    def ev(self, eid: str) -> dict:
        e = self.events[eid]
        if e["archive_status"] == "archived":
            raise RuntimeError("archived event referenced by public page: " + eid)
        return e

    def mv(self, mid: str) -> dict:
        m = self.matches[mid]
        self.ev(m["event_id"])
        return m

    def team_name(self, tid: str) -> str:
        return self.teams.get(tid, {}).get("name", tid)

    def person_name(self, pid: str | None) -> str:
        return self.persons.get(pid, {}).get("display_name", "—") if pid else "—"

    def role_of(self, pid: str, game_id: str = "g_s2_01_1") -> str:
        for st in self.stats:
            if st["person_id"] == pid and st["game_id"] == game_id:
                return st.get("role") or "—"
        return "—"

    def layout(self, title: str, active: str, body: str, desc: str) -> str:
        nav = [("index.html", "首页", "home"), ("event.html", "赛事", "event"),
               ("schedule.html", "赛程", "schedule"), ("players/" + SAMPLE_SLUG + ".html", "选手", "players")]
        nav_html = "".join(
            f'<a class="{"on" if key == active else ""}" href="{self.prefix}{href}">{label}</a>'
            for href, label, key in nav)
        mobile = "".join(
            f'<a class="{"on" if key == active else ""}" href="{self.prefix}{href}">{label}</a>'
            for href, label, key in nav)
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(title)} · 宗师杯</title>
<meta name="description" content="{esc(desc)}"/>
<meta property="og:title" content="{esc(title)} · 宗师杯"/>
<meta property="og:description" content="{esc(desc)}"/>
<meta property="og:type" content="website"/>
<link rel="stylesheet" href="{self.prefix}assets/theme.css"/>
</head>
<body>
<header class="topbar"><div class="topbar-in">
  <a class="brand" href="{self.prefix}index.html"><div class="seal">宗</div><div><b>宗师杯</b><span>学生自己组的擂台 · 数据可追溯</span></div></a>
  <nav class="nav">{nav_html}</nav>
</div></header>
<main class="wrap">
{body}
<footer class="footer">
  宗师杯 · 学生自行组织的王者荣耀国际服赛事（非校队）｜本页为 M1 样板，不是正式赛事公告。<br/>
  数据来源见 <a href="{self.prefix}sources.html">来源与核对</a>；只公开游戏昵称与游戏数据，不公开真实姓名/学校。
  发现错误或希望隐藏数据，请联系 Jason（由运营人工处理）。<br/>
  本页由 Jason 的 AI 小助手（DeepSeek）生成 · 未确认信息标「待核实 / 待公布」。
</footer>
</main>
<nav class="mobile-nav">{mobile}</nav>
</body>
</html>"""

    # ---------- pages ----------
    def page_index(self) -> str:
        pub = [a for a in self.announcements if a["publish_status"] == "published"]
        concept = [e for e in self.public_events.values() if e["publish_status"] == "concept"]
        hist = self.ev("e_s2_01")
        m = self.mv("m_s2_01")
        g = self.games["g_s2_01_1"]
        ann_html = "".join(
            f'<article class="card tight"><h3>{esc(a["title"])}</h3>'
            f'<p class="small" style="margin:4px 0 8px">{esc(a["body"])}</p>'
            f'<span class="badge">公告日期待公布</span></article>'
            for a in pub[:2])
        concept_html = "".join(
            f'<article class="card"><div class="badges">{self.event_state(e)}</div>'
            f'<h3 style="margin-top:8px">{esc(e["title"])}</h3>'
            f'<p class="small">{esc(e["summary"])}</p>'
            f'<p class="small">规则状态：待定 · 赛程：<b>待公布</b> · 报名：未开放（不显示「报名中」）</p>'
            f'<a class="btn ghost small" href="{self.prefix}event.html">查看赛事结构 →</a></article>'
            for e in concept)
        sample = self.persons["p_0002"]
        body = f"""
<section class="hero">
  <div class="eyebrow">宗师杯 · 持续办赛的赛事入口</div>
  <h1>学生自己组的擂台，<br/>下一场等你来。</h1>
  <p class="lead">先看公告与赛程，再找自己的档案和上一场战报。赛程、报名、奖金均以主办方公布为准；没有确认就写「待公布」。</p>
  <div class="badges"><span class="badge gold">A 夜战金 · M1 样板</span><span class="badge">历史战报</span><span class="badge">数据可追溯</span></div>
  <div class="hero-actions">
    <a class="btn" href="{self.prefix}event.html">查看赛事 →</a>
    <a class="btn ghost" href="{self.prefix}players/{SAMPLE_SLUG}.html">样板选手页 →</a>
    <a class="btn ghost" href="{self.prefix}matches/s2-first.html">看上一场战报 →</a>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>最新公告</h2><a href="{self.prefix}event.html">赛事与公告 →</a></div>
  <div class="grid cols2">{ann_html}</div>
</section>

<section class="section">
  <div class="section-head"><h2>下一场比赛</h2><span class="badge warn">赛程待公布</span></div>
  <div class="card">
    <h3>暂无已确认的下一场比赛</h3>
    <p class="small">赛程、日期、报名方式尚未确认。确认后会在此公布；在确认前不显示倒计时、不显示「报名中」。</p>
    <p class="small">查看未来赛事方向 → <a href="{self.prefix}event.html">赛事结构</a></p>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>近期赛果与战报</h2><a href="{self.prefix}schedule.html">赛程与战报 →</a></div>
  <article class="card">
    <div class="badges"><span class="badge">历史赛事 · 已结束</span><span class="badge warn">比赛日期待确认</span><span class="badge">BO1</span></div>
    <h3 style="margin-top:10px">赏金赛第一把 · {esc(self.team_name("t_osu"))} vs {esc(self.team_name("t_champ"))}</h3>
    <div class="score">3<span class="muted"> : </span><span class="lose">17</span></div>
    <p class="small">单局击杀数 · {self.clock_note()} · 胜局 0:1 · 来源：{self.src("src_settle_919","结算面板")} · {self.src("src_base_905","905s")}</p>
    <a class="btn ghost small" href="{self.prefix}matches/s2-first.html">看战报 →</a>
  </article>
</section>

<section class="section">
  <div class="section-head"><h2>未来赛事方向（筹备中，未公布）</h2></div>
  <div class="grid cols2">{concept_html}</div>
</section>

<section class="section">
  <div class="section-head"><h2>选手入口</h2><span class="small">M1 只做 1 个样板选手页</span></div>
  <div class="card">
    <div class="badges"><span class="badge gold">样板选手页</span><span class="badge warn">身份 / 分路待确认</span></div>
    <h3 style="margin-top:8px">{esc(sample["display_name"])} · 铠 · 一场数据</h3>
    <p class="small">KDA 3/3/0 · 参团 100% · 1 场 · 标签：数据不足（仅 1 场）。{self.src("src_settle_919")}</p>
    <a class="btn ghost small" href="{self.prefix}players/{SAMPLE_SLUG}.html">查看样板选手页 →</a>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>二级入口</h2></div>
  <div class="grid cols3">
    <div class="card tight"><h3>来源与核对</h3><p class="small">每个数字点回来源，未确认项单独列出。</p><a class="small" href="{self.prefix}sources.html">查看来源 →</a></div>
    <div class="card tight"><h3>视频与名场面</h3><p class="small">现有剪辑 2 支；待授权确认后接入，本轮只留占位。</p><span class="badge">待授权接入</span></div>
    <div class="card tight"><h3>数据与模型</h3><p class="small">后续接入建模会话已审核的分析；未校准胜率不展示。</p><span class="badge">后续版本</span></div>
  </div>
</section>
"""
        return self.layout("首页", "home", body, "宗师杯：公告、赛程、战报与选手档案")

    def page_event(self) -> str:
        league = self.ev("e_league_concept")
        bounty = self.ev("e_bounty_concept")
        hist = self.ev("e_s2_01")
        lease_ann = [a for a in self.announcements
                     if a["event_id"] == league["event_id"] and a["publish_status"] == "published"]
        rule = self.rulesets[league["ruleset_id"]]
        phase = self.phases["ph_league_preseason"]
        body = f"""
<div class="breadcrumb"><a href="{self.prefix}index.html">首页</a> / 赛事</div>
<section class="hero" style="padding-top:18px">
  <div class="eyebrow">赛事详情 · 样板</div>
  <h1>{esc(league["title"])}</h1>
  <div class="badges">{self.event_state(league)}<span class="badge warn">规则待定</span><span class="badge">阶段：赛前筹备</span></div>
  <p class="lead">{esc(league["summary"])}。这是一个用于展示结构的筹备方案：赛制、阶段、队伍与时间均待讨论，不作为已公布规则。</p>
</section>

<section class="section">
  <div class="section-head"><h2>公告</h2><span class="badge">暂无已发布公告</span></div>
  <div class="notice">该赛事仍为筹备方案，公告草案不对外展示。正式公告发布后，这里会出现时间、报名方式与规则版本；未确认前只写「待公布」。</div>
</section>

<section class="section">
  <div class="section-head"><h2>规则状态</h2><a class="small" href="{self.prefix}sources.html#src_jason_20261031">依据：Jason 任务大纲</a></div>
  <div class="table-wrap"><table>
    <tr><th>项目</th><th>状态</th><th>说明</th></tr>
    <tr><td>活动类别</td><td>长周期正式赛事（方向）</td><td>非已公布赛制</td></tr>
    <tr><td>阶段</td><td>{self.status(phase["window_status"])} {esc(PHASE_KIND.get(phase["kind"], phase["kind"]))}</td><td>是否设季前/常规/季后赛待讨论</td></tr>
    <tr><td>规则集</td><td>{esc(rule["title"])} {self.status(rule["status"])}</td><td>规则版本与细则未定</td></tr>
    <tr><td>组队方式</td><td>待讨论</td><td>固定队 / 临时队 / 其他，未定</td></tr>
    <tr><td>报名</td><td>未开放</td><td>开放前会发公告；未确认信息不展示</td></tr>
    <tr><td>赛程</td><td>待公布</td><td>无确认日期</td></tr>
  </table></div>
  <p class="scroll-hint">← 左右滑动查看完整表格 →</p>
</section>

<section class="section">
  <div class="section-head"><h2>简版赛程</h2><span class="badge warn">赛程待公布</span></div>
  <div class="card tight">
    <p class="small">阶段 1 · 赛前筹备（{esc(PHASE_KIND.get(phase["kind"], phase["kind"]))}）｜ 状态：<b>待公布</b> ｜ 时间：待公布</p>
    <p class="small">阶段 2 及后续：是否设置、如何晋级均待讨论。</p>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>其他赛事方向</h2></div>
  <div class="grid cols2">
    <article class="card"><div class="badges">{self.event_state(bounty)}</div>
      <h3 style="margin-top:8px">{esc(bounty["title"])}</h3>
      <p class="small">{esc(bounty["summary"])}</p>
      <p class="small">拍卖式组队、队长资格、预算单位、队伍数、BO 局数均待设计；本轮不写成确定机制。</p></article>
    <article class="card"><div class="badges">{self.event_state(hist)}<span class="badge warn">日期待确认</span></div>
      <h3 style="margin-top:8px">{esc(hist["title"])}</h3>
      <p class="small">历史赛事，赛制与奖励规则属于当时的历史规则，与未来赏金赛不是同一套规则。</p>
      <p class="small">可查看已整理的 <a href="{self.prefix}matches/s2-first.html">单场战报</a>。</p></article>
  </div>
</section>
"""
        return self.layout("赛事", "event", body, "宗师杯赛事结构：长周期赛事、赏金淘汰赛与历史赛事")

    def page_schedule(self) -> str:
        m = self.mv("m_s2_01")
        g = self.games["g_s2_01_1"]
        hist = self.ev("e_s2_01")
        concept = [e for e in self.public_events.values() if e["publish_status"] == "concept"]
        concept_rows = "".join(
            f'<tr><td>{esc(e["title"])}</td><td><span class="badge warn">筹备方案，尚未公布</span></td>'
            f'<td>赛程待公布</td><td>未开放</td></tr>' for e in concept)
        body = f"""
<div class="breadcrumb"><a href="{self.prefix}index.html">首页</a> / 赛程</div>
<section class="hero" style="padding-top:18px">
  <div class="eyebrow">赛程与战报</div>
  <h1>已结束的比赛，和还没公布的那一场。</h1>
  <p class="lead">有确认日期的比赛才写日期；没有就写「赛程待公布」。下图只列真实状态，不放示范日期或假倒计时。</p>
</section>

<section class="section">
  <div class="section-head"><h2>已结束</h2><span class="badge">历史赛事</span></div>
  <div class="card">
    <div class="badges">{self.event_state(hist)}<span class="badge warn">日期待确认</span><span class="badge">BO1</span></div>
    <h3 style="margin-top:10px">赏金赛第一把 · {esc(self.team_name("t_osu"))} vs {esc(self.team_name("t_champ"))}</h3>
    <p class="small">单局击杀 <b>3 : 17</b> · {self.clock_note()} · 胜局 0:1 · 来源：{self.src("src_settle_919","结算面板")} · {self.src("src_base_905","905s")}</p>
    <a class="btn ghost small" href="{self.prefix}matches/s2-first.html">查看战报 →</a>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>待公布 / 筹备中</h2><span class="badge warn">不构成已确认赛程</span></div>
  <div class="table-wrap"><table>
    <tr><th>赛事</th><th>状态</th><th>赛程</th><th>报名</th></tr>
    {concept_rows}
  </table></div>
  <p class="scroll-hint">← 左右滑动查看完整表格 →</p>
  <p class="small" style="margin-top:10px">赛程以主办方公告为准；筹备方案不显示「报名中」，不显示倒计时。</p>
</section>
"""
        return self.layout("赛程", "schedule", body, "宗师杯赛程：已结束比赛与待公布状态")

    def page_match(self) -> str:
        m = self.mv("m_s2_01")
        g = self.games["g_s2_01_1"]
        hist = self.ev("e_s2_01")
        teams = [("t_osu", "team_a"), ("t_champ", "team_b")]
        rows = []
        for tid, key in teams:
            members = [st for st in self.stats if st["team_id"] == tid]
            for st in members:
                p = self.persons[st["person_id"]]
                rows.append(
                    f'<tr><td>{esc(self.team_name(tid))}</td><td>{esc(p["display_name"])}</td>'
                    f'<td>{esc(st["role"] or "—")} {self.status(st["role_status"])}</td>'
                    f'<td>{st["kills"]}/{st["deaths"]}/{st["assists"]}</td>'
                    f'<td>{esc(str(st["participation"]) if st["participation"] is not None else "—")}%</td>'
                    f'<td>{self.src("src_settle_919")}</td></tr>')
        kills = [t for t in self.timeline if t["type"] == "kill"]
        towers = [t for t in self.timeline if t["type"] == "tower"]
        base = [t for t in self.timeline if t["type"] == "base"]
        def timeline_html(items):
            out = []
            for t in items:
                who = self.person_name(t["person_id"]) if t["person_id"] else esc(self.team_name(t["team_id"])) if t["team_id"] else "归属待确认"
                out.append(
                    f'<li><time>{esc(t["clock"])}</time><div>{esc(t["description"])}'
                    f'<span class="small">（{who}）</span>'
                    f'{self.status(t["clock_status"]) if t["clock_status"] != "confirmed" else ""}'
                    f'{self.src(t["evidence_ref_id"])}</div></li>')
            return "".join(out)
        body = f"""
<div class="breadcrumb"><a href="{self.prefix}index.html">首页</a> / <a href="{self.prefix}schedule.html">赛程</a> / 战报</div>
<section class="hero" style="padding-top:16px">
  <div class="badges">{self.event_state(hist)}<span class="badge warn">比赛日期待确认</span><span class="badge">BO1</span></div>
  <h1 style="margin-top:10px">赏金赛第一把</h1>
  <p class="muted">{esc(self.team_name("t_osu"))} vs {esc(self.team_name("t_champ"))} · 历史赛事 · 规则以当时口径为准</p>
  <div class="score-label">单局击杀数</div>
  <div class="score">3<span class="muted"> : </span><span class="lose">17</span></div>
  <p class="small">胜局 0 : 1 · {self.clock_note()} · 来源：{self.src("src_settle_919","结算面板")} · {self.src("src_base_905","905s")} · 比赛日期待确认</p>
</section>

<section class="section">
  <div class="section-head"><h2>双方数据</h2><span class="badge warn">一局样本 · 分路待确认</span></div>
  <div class="table-wrap"><table>
    <tr><th>阵营</th><th>昵称</th><th>分路</th><th>K / D / A</th><th>参团率</th><th>来源</th></tr>
    {''.join(rows)}
  </table></div>
  <p class="scroll-hint">← 左右滑动查看完整表格 →</p>
  <p class="small" style="margin-top:10px">分路来自现有档案，标注为「待确认」；参团率口径以结算面板为准。</p>
</section>

<section class="section">
  <div class="section-head"><h2>击杀时间线</h2><span class="small">时间码冲突项已标「待核实」</span></div>
  <div class="card tight"><ul class="timeline">{timeline_html(kills)}</ul></div>
</section>

<section class="section">
  <div class="section-head"><h2>推塔时间线</h2><span class="badge warn">需复核原帧</span></div>
  <div class="card tight"><ul class="timeline">{timeline_html(towers)}</ul></div>
  <p class="small" style="margin-top:8px">推塔时间来自地图教程例题（map_kit），不是逐帧确证；原帧复核后再去掉「待核实」。</p>
</section>

<section class="section">
  <div class="section-head"><h2>客观事实与已确认口径</h2></div>
  <div class="note">
    · 全队 3 个人头均来自放闪的秋的铠（{self.highlight_text()}；第一头口径待统一）。<br/>
    · 对方打野暃 8/0/6、中路沈梦溪 6/1/7（结算面板）。<br/>
    · 6:08 之前结束 → 速通奖励按 2.6 倍结算；队内评选 MVP 为猫猫（沈梦溪），额外 50%——这两项为已确认口径，具体金额与凭据待补，页面不展示金额。{self.src("src_fact_ledger")}
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>复盘视频</h2><span class="badge">待授权接入</span></div>
  <div class="videoph">视频模块待授权后接入（现有剪辑 2 支：四分钟复盘 57.6s、开头样片 57s）。<br/>公开前需确认音乐/画面/选手授权；本轮不嵌入未授权视频。</div>
</section>

<section class="section">
  <div class="section-head"><h2>来源</h2><a class="small" href="{self.prefix}sources.html">来源与核对总表 →</a></div>
  <p class="small">结算面板、身份与事实修正、map_kit、事实台账。未确认项见 <a href="{self.prefix}sources.html">来源页</a>。</p>
</section>
"""
        return self.layout("赏金赛第一把战报", "schedule", body, "赏金赛第一把：3:17、最后可见时钟 06:03、时间线与双方数据")

    def page_player(self) -> str:
        self.ev("e_s2_01")
        p = self.persons["p_0002"]
        st = next(s for s in self.stats if s["person_id"] == "p_0002")
        kills = [t for t in self.timeline if t["type"] == "kill" and t["person_id"] == "p_0002"]
        g = self.games["g_s2_01_1"]
        timeline_html = "".join(
            f'<li><time>{esc(t["clock"])}</time><div>{esc(t["description"])}'
            f'{self.status(t["clock_status"]) if t["clock_status"] != "confirmed" else ""}'
            f'{self.src(t["evidence_ref_id"])}</div></li>' for t in kills)
        body = f"""
<div class="breadcrumb"><a href="{self.prefix}index.html">首页</a> / <a href="{self.prefix}players/{SAMPLE_SLUG}.html">选手</a> / 放闪的秋</div>
<section class="player-head">
  <div class="avatar">铠</div>
  <div>
    <h1>{esc(p["display_name"])}</h1>
    <div class="muted">我方 · 分路待确认 · 身份待确认 · 本场英雄：铠</div>
    <div class="badges"><span class="badge gold">M1 样板选手页</span><span class="badge warn">身份 / 分路待确认</span></div>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>本场数据</h2><span class="small">1 场 · 赏金赛第一把（历史）</span></div>
  <div class="kv">
    <div class="item"><span>K / D / A</span><b>{st["kills"]}/{st["deaths"]}/{st["assists"]}</b></div>
    <div class="item"><span>参团率</span><b>{fmt_num(st["participation"])}%</b></div>
    <div class="item"><span>场次</span><b>1</b></div>
    <div class="item"><span>本场结果</span><b>负</b></div>
  </div>
  <p class="small" style="margin-top:10px">来源：{self.src("src_settle_919","结算面板")} · 分路：{esc(st["role"] or "—")} {self.status(st["role_status"])} · 仅为 1 场，不代表长期实力。</p>
</section>

<section class="section">
  <div class="section-head"><h2>风格标签</h2><span class="badge warn">数据不足</span></div>
  <div class="card tight">
    <p class="small">标签：<b>数据不足（仅 1 场）</b>。按项目规则，只发布 5 组阈值全中的稳定标签；一局样本不生成公开标签。</p>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>数据印象</h2></div>
  <div class="note">全队 3 个人头都在他手上（{self.highlight_text()}），但 3 次死亡、0 助攻——一局样本，不是实力评价。</div>
</section>

<section class="section">
  <div class="section-head"><h2>高光时间线</h2><span class="small">只列可归因事件</span></div>
  <div class="card tight"><ul class="timeline">{timeline_html}</ul></div>
  <p class="small" style="margin-top:8px">第一头时间存在 01:56 / 01:57 两种记录，页面标「待核实」；统一口径后去掉标注。</p>
</section>

<section class="section">
  <div class="section-head"><h2>比赛记录</h2></div>
  <div class="card tight">
    <p class="small">1 场 · 赏金赛第一把 · 单局击杀 3 : 17 · {self.clock_note()} · 负。</p>
    <a class="btn ghost small" href="{self.prefix}matches/s2-first.html">查看完整战报 →</a>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>视频与名场面</h2><span class="badge">待授权接入</span></div>
  <div class="videoph">选手相关剪辑待视频会话提供并获授权后接入。<br/>本轮不嵌入未授权视频，不占位假视频。</div>
</section>

<section class="section">
  <div class="section-head"><h2>选手自述</h2><span class="badge">未填写</span></div>
  <div class="card tight">
    <p class="small">「本人还没写」。自述、代表英雄、想被记住的名场面等将在审核后展示；只公开游戏昵称与游戏数据，不公开真实姓名/学校。</p>
  </div>
  <div class="sharebox">
    <button class="btn ghost small" type="button" onclick="copyLink()">复制本页链接</button>
    <span class="copy-hint" id="copyHint"></span>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>来源与说明</h2><a class="small" href="{self.prefix}sources.html">来源与核对总表 →</a></div>
  <p class="small">KDA/参团：结算面板；时间线：身份与事实修正 + 画面核对；推塔：map_kit（需复核）。<br/>
  数据不确定性、身份合并候选、分路口径见 <a href="{self.prefix}sources.html">来源页</a> 的「待核实清单」。</p>
</section>
<script>
function copyLink(){{
  const url = location.href.split('#')[0];
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(url).then(function(){{
      document.getElementById('copyHint').textContent = '已复制链接';
    }}, function(){{ document.getElementById('copyHint').textContent = '复制失败，请手动复制地址栏'; }});
  }} else {{
    document.getElementById('copyHint').textContent = '复制失败，请手动复制地址栏';
  }}
}}
</script>
"""
        return self.layout("放闪的秋 · 选手档案", "players", body, "放闪的秋：赏金赛第一把一局数据、时间线与来源")

    def page_sources(self) -> str:
        rows = "".join(
            f'<tr id="{esc(s["source_id"])}"><td>{esc(s["source_id"])}</td><td>{esc(s["kind"])}</td>'
            f'<td>{esc(s["locator"])}</td><td>{esc(s.get("source_date") or "—")}</td>'
            f'<td>{esc(s.get("captured_at") or "—")}</td><td>{self.status(s["verified_status"])}</td>'
            f'<td class="small">{esc(s.get("notes") or "")}</td></tr>'
            for s in self.d["sources"])
        body = f"""
<div class="breadcrumb"><a href="{self.prefix}index.html">首页</a> / 来源与核对</div>
<section class="hero" style="padding-top:18px">
  <div class="eyebrow">来源与核对</div>
  <h1>每个数字，都尽量点得回来源。</h1>
  <p class="lead">本页列出 M1 样板用到的数据来源、确认状态与待核实项。未确认的信息不写成确定事实；样板仍受「只公开游戏昵称与游戏数据」约束。</p>
</section>

<section class="section">
  <div class="section-head"><h2>来源等级</h2></div>
  <div class="grid cols3">
    <div class="card tight"><h3>A · 逐数字可追</h3><p class="small">比分、击杀/推塔事件、视频时长：每条给来源 + 时间码/场次。</p></div>
    <div class="card tight"><h3>B · 逐模块可追</h3><p class="small">S1 六维、英雄榜：给表名 + 源日期 + 抓取日期。</p></div>
    <div class="card tight"><h3>C · 仅汇总</h3><p class="small">跨赛事计数：给数据文件 + 计数口径，标「计数待身份确认」。</p></div>
  </div>
</section>

<section class="section">
  <div class="section-head"><h2>来源表</h2><span class="small">本样板用到的全部来源</span></div>
  <div class="table-wrap"><table>
    <tr><th>来源 ID</th><th>类型</th><th>定位</th><th>源日期</th><th>抓取日期</th><th>确认状态</th><th>用途</th></tr>
    {rows}
  </table></div>
  <p class="scroll-hint">← 左右滑动查看完整表格 →</p>
  <p class="small" style="margin-top:10px">部分资料在主项目目录（未随本仓库发布），公开前需执行端核对；本页不暴露本机绝对路径。</p>
</section>

<section class="section">
  <div class="section-head"><h2>待核实清单</h2><span class="badge warn">不写成确定事实</span></div>
  <div class="table-wrap"><table>
    <tr><th>项</th><th>现状</th><th>处理</th></tr>
    <tr><td>一血时间</td><td>00:41 / 00:44–00:45 两套记录</td><td>标「待核实」，统一口径后更新</td></tr>
    <tr><td>我方第一头</td><td>01:57 / 01:56 两套记录</td><td>标「待核实」</td></tr>
    <tr><td>S2 分路</td><td>候选、未人工确认</td><td>标「待确认」</td></tr>
    <tr><td>比赛日期 / 正式名称</td><td>未确认</td><td>显示「日期待确认」，不写死</td></tr>
    <tr><td>推塔时间</td><td>地图教程例题，需复核原帧</td><td>标「待核实」</td></tr>
    <tr><td>奖金金额 / 50、67 项目名</td><td>未核实</td><td>不展示金额，只写 2.6× / MVP 额外 50%</td></tr>
    <tr><td>身份合并</td><td>候选、未人工确认</td><td>不合并、不覆盖；页面标「身份待确认」</td></tr>
    <tr><td>视频与选手资料授权</td><td>公开前需确认</td><td>未授权前不嵌入视频；公开范围另审</td></tr>
  </table></div>
  <p class="scroll-hint">← 左右滑动查看完整表格 →</p>
</section>

<section class="section">
  <div class="section-head"><h2>隐私与纠错</h2></div>
  <div class="note">
    只公开游戏昵称与游戏数据，不公开真实姓名、学校、联系方式、住址或照片。<br/>
    选手可要求隐藏或删除自己的页面/数据；发现数字有误，请联系 Jason，由运营人工核对后更新。<br/>
    网站公开、源码公开、选手资料公开是三个不同范围，分别检查，不自动视为已授权。
  </div>
</section>
"""
        return self.layout("来源与核对", "sources", body, "宗师杯 M1 样板的数据来源、确认状态与待核实清单")

    def page_share_card(self) -> str:
        p = self.persons["p_0002"]
        st = next(s for s in self.stats if s["person_id"] == "p_0002")
        kills = [t for t in self.timeline if t["type"] == "kill" and t["person_id"] == "p_0002"]
        ords = ["一", "二", "三", "四", "五"]
        tl_rows = "".join(
            f'<div><time>{esc(t["clock"])}</time><span>全队第{ords[i]}头（铠）'
            f'{" · 时间待核实" if t["clock_status"] != "confirmed" else ""}</span></div>'
            for i, t in enumerate(kills))
        return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<title>分享卡 · 放闪的秋</title>
<style>
*{{box-sizing:border-box;margin:0}}
html{{background:#0a0d14}}body{{width:720px;height:960px;zoom:1.5;overflow:hidden;position:relative;background:radial-gradient(110% 60% at 50% 0%,#2b2312 0%,#0a0d14 60%) no-repeat,#0a0d14;color:#eef1f6;font-family:"Microsoft YaHei","Noto Sans SC",sans-serif;padding:46px 48px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;justify-content:space-between}}
.brand{{display:flex;align-items:center;gap:14px}}
.seal{{width:58px;height:58px;border:3px solid #e8a832;border-radius:12px;display:grid;place-items:center;font:700 28px/1 "STKaiti","KaiTi",serif;color:#e8a832}}
.brand b{{font-size:30px;letter-spacing:4px;display:block;line-height:1.1}}
.brand span{{font-size:14px;color:#aab1c2;letter-spacing:1px}}
.tag{{font-size:13px;color:#e8a832;border:1px solid rgba(232,168,50,.5);border-radius:999px;padding:5px 12px;white-space:nowrap}}
.player{{display:flex;align-items:center;gap:18px;margin-top:46px}}
.avatar{{width:96px;height:96px;flex:none;border-radius:20px;border:1px solid rgba(232,168,50,.45);background:radial-gradient(circle at 30% 20%,rgba(232,168,50,.4),rgba(20,26,38,.95));display:grid;place-items:center;font:700 34px/1 "STKaiti","KaiTi",serif;color:#e8a832}}
h1{{font-size:52px;letter-spacing:2px;line-height:1.1}}
.sub{{font-size:16px;color:#aab1c2;margin-top:6px}}
.badges{{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}}
.badge{{font-size:13px;color:#f2b95c;border:1px solid rgba(242,185,92,.4);background:rgba(242,185,92,.08);border-radius:999px;padding:4px 12px}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:26px}}
.stat{{background:#0e1320;border:1px solid #263044;border-radius:14px;padding:14px 10px;text-align:center}}
.stat span{{display:block;font-size:13px;color:#aab1c2}}
.stat b{{display:block;font-family:Consolas,monospace;font-size:26px;color:#f6cf7a;margin-top:2px}}
.note{{margin-top:24px;background:rgba(232,168,50,.07);border-left:4px solid #e8a832;border-radius:10px;padding:14px 16px;font-size:15px;line-height:1.7;color:#dde1e9}}
.tl{{margin-top:18px}} .tl h2,.match h2{{font-size:15px;color:#e8a832;letter-spacing:2px;margin-bottom:6px}} .match{{margin-top:16px;font-size:14px;color:#dde1e9;border-top:1px dashed #263044;padding-top:12px}}
.tl h2{{font-size:15px;color:#e8a832;letter-spacing:2px;margin-bottom:8px}}
.tl div{{display:flex;gap:14px;font-size:15px;padding:9px 0;border-top:1px dashed #263044}}
.tl time{{font-family:Consolas,monospace;color:#f6cf7a;min-width:58px}}
.foot{{position:absolute;left:48px;right:48px;bottom:34px;padding-top:10px;border-top:none;font-size:12.5px;color:#aab1c2;line-height:1.8}}
.foot b{{color:#e8a832;font-weight:600}}
.qr{{width:120px;height:120px;border:1px dashed #263044;border-radius:10px;display:grid;place-items:center;text-align:center;font-size:11px;color:#aab1c2;line-height:1.5}}
</style></head>
<body>
<div class="top">
  <div class="brand"><div class="seal">宗</div><div><b>宗师杯</b><span>学生自己组的擂台</span></div></div>
  <div class="tag">M1 样板 · 非正式海报</div>
</div>
<div class="player">
  <div class="avatar">铠</div>
  <div><h1>放闪的秋</h1><div class="sub">我方 · 分路待确认 · 本场英雄：铠</div></div>
</div>
<div class="badges"><span class="badge">身份 / 分路待确认</span><span class="badge">1 场样本</span><span class="badge">标签：数据不足</span></div>
<div class="stats">
  <div class="stat"><span>K / D / A</span><b>{st["kills"]}/{st["deaths"]}/{st["assists"]}</b></div>
  <div class="stat"><span>参团率</span><b>{fmt_num(st["participation"])}%</b></div>
  <div class="stat"><span>场次</span><b>1</b></div>
  <div class="stat"><span>本场结果</span><b>负</b></div>
</div>
<div class="note">全队 3 个人头都在他手上（{self.highlight_text()}），但 3 次死亡、0 助攻——一局样本，不是实力评价。</div>
<div class="tl"><h2>高光时间线</h2>
  {tl_rows}
</div>
<div class="match"><h2>比赛记录</h2><div>赏金赛第一把 · 单局击杀 <b>3 : 17</b> · {self.clock_note()} · 负 · BO1</div></div>
<div class="foot">
  <b>数据来源：</b>赏金赛第一把结算面板 + 身份与事实修正 + map_kit（推塔）；1 场样本，不代表长期实力。<br/>
  <b>只公开游戏昵称与游戏数据</b>，不公开真实姓名/学校；未确认信息标「待核实」。<br/>
  <div style="display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:12px">
    <div>本卡由 Jason 的 AI 小助手（DeepSeek）生成<br/>线上预览地址待开通（模板样板）</div>
    <div class="qr">二维码<br/>待上线</div>
  </div>
</div>
</body></html>"""

    def build(self) -> None:
        SITE.mkdir(parents=True, exist_ok=True)
        (SITE / "assets").mkdir(exist_ok=True)
        (SITE / "matches").mkdir(exist_ok=True)
        (SITE / "players").mkdir(exist_ok=True)
        (SITE / "assets" / "theme.css").write_text(CSS, encoding="utf-8")
        self.prefix = ""
        (SITE / "index.html").write_text(self.page_index(), encoding="utf-8")
        (SITE / "event.html").write_text(self.page_event(), encoding="utf-8")
        (SITE / "schedule.html").write_text(self.page_schedule(), encoding="utf-8")
        (SITE / "sources.html").write_text(self.page_sources(), encoding="utf-8")
        self.prefix = "../"
        (SITE / "matches" / "s2-first.html").write_text(self.page_match(), encoding="utf-8")
        (SITE / "players" / f"{SAMPLE_SLUG}.html").write_text(self.page_player(), encoding="utf-8")
        self.prefix = ""
        (SITE / "share-card.html").write_text(self.page_share_card(), encoding="utf-8")
        print("built:", SITE)


if __name__ == "__main__":
    from prepare_data import validate
    data = json.loads(DATA.read_text(encoding="utf-8"))
    validate(data)
    Site(data).build()
